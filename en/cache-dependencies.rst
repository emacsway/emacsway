
About problems of cache invalidation. Cache tagging.
====================================================


.. post::
   :language: en
   :tags: cache
   :category:
   :author: Ivan Zakrevsky

About my experience of solving problems in cache invalidation, and about principles of the library `cache-dependencies`_.

.. contents:: Contents


The problem of cache dependencies
=================================

When you edit the data of some model, you must also remove all dependent caches, that contains the data of this model.
For example, when you edit instance of Product model, which presents on the cached main page of firm, you have to invalidate this cache too.
Another case, - if the data (for example, last_name) of User model has been updated, you have to invalidate all caches of user's posts, contained the last_name.

Usually, the pattern `Observer`_ (or its variety, pattern Multicast) is responsible for cache invalidation.
This means, the event handler should be aware of all dependent components, that violates encapsulation.

And then cache tagging (i.e. marking cache by tags) comes to the rescue.
For example, main page can be marked by tag ``product.id:635``.
All user's posts can be marked by tag ``user.id:10``.
Post lists can be marked by composite tag, composed of selection criteria, for example ``type.id:1;category.id:15;region.id:239``.

Now it's enough to invalidate the tag, in order to invalidate all dependent caches.
This approach is not new, and widely used in other programming languages.
At one time it was even implemented in memcache, see `memcached-tag <http://code.google.com/p/memcached-tag/>`_.

See also:

- `Cache dependency in wheezy.caching <https://pypi.python.org/pypi/wheezy.caching>`_
- `TaggableInterface of ZF <http://framework.zend.com/manual/current/en/modules/zend.cache.storage.adapter.html#the-taggableinterface>`_
- `TagDependency of YII framework <http://www.yiiframework.com/doc-2.0/yii-caching-tagdependency.html>`_
- `Dklab_Cache: правильное кэширование — тэги в memcached, namespaces, статистика <http://dklab.ru/lib/Dklab_Cache/>`_


Should overhead be at cache reading, or at cache creation?
==========================================================

How to implement invalidation of caches dependent on the tag?
There are exist two options:

\1. Destroy physically all dependent caches on the tag invalidation.
Implementation of this approach requires some overhead on the cache creation to add key of the cache into the cache list (or set) of tag (for example, using `SADD <http://redis.io/commands/sadd>`_).
The disadvantage is that the invalidation of too many dependent caches takes some time.

\2. Just change the version of tag on the tag invalidation.
Implementation of this approach requires some overhead on the cache reading to compare version of each tag of the cache with the actual tag version.
So, the cache should contain all tag versions on creation.
If any tag version is expired on the cache reading, the cache is invalid.
The advantage of this approach is immediate invalidation of the tag and all dependent caches.
Можно не бояться вытеснения из хранилища закэшированной информации о версии метки по LRU_ принципу, так как метки запрашиваются намного чаще самого кэша.

I chose the second option.


Tagging of nested caches
========================

Because tags are comparing at the moment of cache reading, let's imagine, what happens, when one cache will be nested in other cache.
Multi-level cache is not uncommon.
In this case, the tags of inner cache will never be verified, and outer cache will remain with outdated data.
At the moment of creation the outer cache, it must add all tags of inner cache into own tag list.
If we pass tags from inner cache to outer cache it in explicit way, it violates encapsulation!
So, cache system must keep track the relations between all nested caches, and pass automatically all tags from an inner cache to outer cache.


Problems of replication
=======================

When tag has been invalidated, a concurrent thread/process can recreate a dependent cache with stale data from slave, in period of time between cache invalidation and slave updating.

The best solution to avoid this problem is lock the tag for cache creation until slave will be updated.
But, first, this implies a certain overhead, and secondly, all threads (including current one) continue to read stale data from the slave (unless reading from master specified explicitly).

A compromise solution can be simple re-invalidation of the tag after period of time when the slave is guaranteed to be updated.

By **tag lock** I mean the bypass of creation a cache, which dependent on the tag, by concurrent threads, but not locking concurrent threads until the tag will be released.

Because tag lock algorithm is assigned to a separate interface, it's possible to implement any other algorithm, including `Pessimistic Offline Lock`_ or `Mutual Exclusion`_, as it's implemented, for example, in `wheezy.caching.patterns.OnePass <https://bitbucket.org/akorn/wheezy.caching/src/586b4debff62f885d97e646f0aa2e5d22d088bcf/src/wheezy/caching/patterns.py?at=default&fileviewer=file-view-default#patterns.py-348>`__).

Slave updating can sometimes take 8 seconds and more. Locking of concurrent threads is too expensive for this period of time, and it's almost impossible in web-applications. There is two reasons:

\1. The increase in the number of waiting threads can lead to memory overuse and too many database connection error.
\2. Excessive client waiting for a response from the server (the client can simply leave without waiting for a response).

However, in some (although rare) cases, the Mutex is the only possible option.

In my practice, I have met approach cache regeneration instead of removing/invalidation.
This approach entail ineffective memory usage (in case LRU_ principle).
К тому же, он не решает проблему сложности инвалидации и по сути мало чем отличается от обычного удаления кэша, возлагая всю сложность на само приложение.
Так же он таит множество потенциальных баг.
Например, он чувствителен к качеству ORM, и если ORM не приводит все атрибуты инстанции модели к нужному типу при сохранении, то в кэш записываются неверные типы данных.
Мне приходилось видеть случай, когда атрибут даты записывался к кэш в формате строки, в таком же виде, в каком он пришел от клиента.
Хотя он и записывался в БД корректно, но модель не делала приведение типов без дополнительных манипуляций при сохранении (семантическое сопряжение).


.. _cache-dependencies: https://bitbucket.org/emacsway/cache-dependencies

.. _Deadlock: https://en.wikipedia.org/wiki/Deadlock
.. _Decorator: https://en.wikipedia.org/wiki/Decorator_pattern
.. _Isolation: https://en.wikipedia.org/wiki/Isolation_(database_systems)
.. _LRU: https://en.wikipedia.org/wiki/Cache_replacement_policies#LRU
.. _Mutual Exclusion: https://en.wikipedia.org/wiki/Mutual_exclusion
.. _Observer: https://en.wikipedia.org/wiki/Observer_pattern
.. _Server Side Includes: https://en.wikipedia.org/wiki/Server_Side_Includes
.. _Strategy: https://en.wikipedia.org/wiki/Strategy_pattern
.. _Thundering Herd: http://en.wikipedia.org/wiki/Thundering_herd_problem

.. _ActiveRecord: http://www.martinfowler.com/eaaCatalog/activeRecord.html
.. _Identity Map: http://martinfowler.com/eaaCatalog/identityMap.html
.. _DataMapper: http://martinfowler.com/eaaCatalog/dataMapper.html
.. _Pessimistic Offline Lock: http://martinfowler.com/eaaCatalog/pessimisticOfflineLock.html
.. _Unit of Work: http://martinfowler.com/eaaCatalog/unitOfWork.html


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

When some data has been updated, all dependent caches should be reset.
Suppose, the cache of main page of a company site contains an instance of Product model.
When the instance of Product model has been updated, the cache should be updated too.
Another example, when attributes of User model (for example, last_name) has been updated, all caches of posts of the user, contained the last_name, should be reset too.

Usually, the pattern `Observer`_ (or its variety pattern Multicast) is responsible for the cache invalidation.
But even in this case the invalidation logic becomes too complicated, the achieved accuracy is too low, the `Coupling`_ is growing fast, and encapsulation is disclosed.

The solution of the issue can be cache tagging (i.e. marking cache by tags).
For example, the cache of main page can be marked by tag ``product.id:635``.
The all user's posts can be marked by tag ``user.id:10``.
Post lists can be marked by composite tag, composed of selection criteria, for example ``type.id:1;category.id:15;region.id:239``.

Now it's enough to invalidate a tag to invalidate all dependent caches.
This approach is not new, and widely used in other programming languages.
At one time it was even implemented in memcache, see `memcached-tag <http://code.google.com/p/memcached-tag/>`_.

See also:

- `Cache dependency in wheezy.caching <https://pypi.python.org/pypi/wheezy.caching>`_
- `TaggableInterface of ZF <http://framework.zend.com/manual/current/en/modules/zend.cache.storage.adapter.html#the-taggableinterface>`_
- `TagDependency of YII framework <http://www.yiiframework.com/doc-2.0/yii-caching-tagdependency.html>`_
- `Dklab_Cache: правильное кэширование — тэги в memcached, namespaces, статистика <http://dklab.ru/lib/Dklab_Cache/>`_


Overhead of cache reading vs overhead of cache creation
=======================================================

How to implement invalidation of caches dependent on the tag?
There are exist two options:

\1. Destroy physically all dependent caches on the tag invalidation.
Implementation of this approach requires some overhead on the cache creation to add key of the cache into the cache list (or set) of the tag (for example, using `SADD <http://redis.io/commands/sadd>`_).
The disadvantage is that the invalidation of too many dependent caches takes some time.

\2. Just change the version of tag on the tag invalidation.
Implementation of this approach requires some overhead on the cache reading to compare version of each tag of the cache with the actual tag version.
So, the cache should contain all tag versions on the cache creation.
If any tag version is expired on the cache reading, the cache is invalid.
The advantage of this approach is immediate invalidation of the tag and all dependent caches.
Another advantage is that premature discarding of a tag info is not possible (using LRU_), because the tag info is read mush often than dependent caches.

I've chose the second option.


Tagging of nested caches
========================

Because tags are verified at the moment of cache reading, let's imagine, what happens, when one cache will be nested in other cache.
Multi-level cache is not so rarely.
In this case, the tags of inner cache will never be verified, and outer cache will alive with outdated data.
At the moment of creation the outer cache, it must accept the all tags from the inner cache into own tag list.
If we pass the tags from the inner cache to the outer cache in an explicit way, it violates encapsulation!
So, cache system must keep track the relations between all nested caches, and pass automatically all tags from an inner cache to its outer cache.


Problems of replication
=======================

When tag has been invalidated, a concurrent thread/process can recreate a dependent cache with outdated data from slave, before slave will be updated.

The best solution of this problem is a :ref:`locking the tag <tags-lock-en>` for cache creation until slave will be updated.
But, first, this implies a certain overhead, and secondly, all threads (including current one) continue to read stale data from the slave (unless reading from master specified explicitly).

A compromise solution can be simple re-invalidation of the tag after period of time when the slave is guaranteed to be updated.

I saw also an approach of cache regeneration instead of removing/invalidation.
This approach entail ineffective memory usage (in case LRU_ principle).
Also, this approach does not resolve the problem of complexity of invalidation logic.
Usualy, this approach is the cause of a lot of bugs.
For example, it requires to use a high quality ORM.
Some ORMs does not perform type conversion of instance attributes on save, therefore, the cache can be wrong (for example, there can be a string instead of a datetime instance).
I saw such case in my practice, the cache saved the string from the HTTP-client instead of the datatime instance. Although the data had been saved correctly, the model logic didn't performed type conversion until some another method had been called (semantic coupling).


.. update:: Nov 10, 2016

    Added description of implementation of tag locking.


.. _tags-lock-en:

Implementation of tag locking
=============================

The main purpose of tag locking is a preventing of substitution of actual data by outdated data by concurent threads/processes, if it's needed by transaction isolation level or a delay of replication.

The tag locking is implemented by library as preventing the dependent cache creation by concurent threads/processes while the tag is locked.

Why was not implemented a `Pessimistic Offline Lock`_ or `Mutual Exclusion`_?
This is a :ref:`resonable <thundering-herd-en>` question, because the cached logic can be too resource intensive.
This implementation requires concurent threads/processes are waiting untile the locked tag will be released.


Constructive obstacle to implementing pessimistic locking
---------------------------------------------------------

The main purpose of the library is cache invalidation.

Suppose, the process P1 has begun transaction with isolation level of "Repeatable read".

Then the process P2 has begun the transaction, updated data in the DB, invalidated tag T1, and ascuired the lock for the tag T1 until the transaction will be commited.

Process P1 are trying to read the cache with key C1, which is tagged by the tag T1, and is not valid anymore.
Not being able to read the invalid cache C1, the process P1 receives the outdated data from the DB (remember, the transaction isolation level is "Repeatable read").
Then the process P1 are trying to create the cache C1, and waiting while the tag T1 will be released.

When the transaction of process P2 is commited, the process P2 releases the tag T1.
Then the process P1 writes the outdated data into the cache C1.
There is no ane sense from this locking.

But what will be happened, if we check the status of tag T1 on the cache reading (not writing)?
Can this approach to change something?

Yes, it can.
First, it adds an overhead to reading logic.
The second, it can has an effect if transaction isolation level is not higher than "Read committed".
For the transaction isolation level "Repeatable read" (which is default for some DB, and at least required for the correct work of pattern `Identity Map`_) and higher, it does not has any effect.
In this case, the process P2 would be locked before the transaction beginning.

Thus, this solution would be partial, not universal, and would contain an uncontrolled dependence.
For 2 from 4 of transaction isolation level it would not work.


Accompanying obstacle to implementing pessimistic locking
---------------------------------------------------------

Except the constructive obstacle to implementing pessimistic locking, there is also some other obstacles.

The library is focused mainly on web applications.
Waiting for parallel process until the end of the transaction, or until the slave is updated, which in some cases can take 8 seconds or more, is practically not feasible in web applications.

There is 3 main reasons:

- Для веб-приложения важна быстрота отклика, так как клиент может просто не дождаться ответа.
- Нет смысла ожидать создание кэша более, чем требуется времени на само создание кэша.
- Рост количества ожидающих потоков может привести к перерасходу памяти, или доступных воркеров сервера, или исчерпанию максимально допустимого числа коннектов к БД или других ресурсов.

Так же возникла бы проблема с реализацией, поскольку корректно заблокировать все метки одним запросом невозможно.

- Во-первых, для блокировки метки нужно использовать метод ``cache.add()`` вместо ``cache.set_many()``, чтобы гарантировать атомарность проверки существования и создания кэша.
- Во-вторых, каждую метку нужно блокировать отдельным запросом, что увеличило бы накладные расходы.
- В-третьих, поодиночное блокирование чревато взаимной блокировкой (Deadlock_), вероятность которой можно заметно сократить с помощью топологической сортировки.

Отдельно стоит упомянуть возможность `блокировки строк в БД <https://www.postgresql.org/docs/9.5/static/explicit-locking.html>`__ при использовании выражения `SELECT FOR UPDATE <https://www.postgresql.org/docs/9.5/static/sql-select.html#SQL-FOR-UPDATE-SHARE>`_. Но это будет работать только в том случае, если обе транзакции используют выражение `SELECT FOR UPDATE`_, в `противном случае <https://www.postgresql.org/docs/9.5/static/transaction-iso.html#XACT-READ-COMMITTED>`__:

    When a transaction uses this isolation level, a SELECT query (without a FOR UPDATE/SHARE clause) sees only data committed before the query began; it never sees either uncommitted data or changes committed during query execution by concurrent transactions. In effect, a SELECT query sees a snapshot of the database as of the instant the query begins to run.

Однако, выборку для модификации не имеет смысла кэшировать (да и вообще, в веб-приложениях ее мало кто использует, так как этот вопрос перекрывается уже вопросом организации бизнес-транзакций), соответственно, ее блокировка мало чем может быть полезна в этом вопросе. К тому же она не решает проблему репликации.


.. _thundering-herd-en:

Thundering herd
===============

Но что делать, если закэшированная логика действительно очень ресурсоемка?

Dogpile известен так же как `Thundering Herd`_ effect или cache stampede.

Ответ прост, - пессимистическая блокировка. Только не меток кэша, а ключа кэша (или группы связанных ключей, см. `Coarse-Grained Lock`_, особенно при использовании агрегирования запросов).
Потому что при освобождении блокировки кэш должен быть гарантированно создан (а кэш и метки связаны отношением many to many).

Блокировка должна охватывать весь фрагмент кода от чтения кэша до его создания.
Она решает другую задачу, которая не связана с инвалидацией.

Существует ряд решений для реализации такой блокировки, вот только некоторые из них:

- `wheezy.caching.patterns.OnePass <https://bitbucket.org/akorn/wheezy.caching/src/586b4debff62f885d97e646f0aa2e5d22d088bcf/src/wheezy/caching/patterns.py?at=default&fileviewer=file-view-default#patterns.py-348>`_
- `memcached_lock <https://pypi.python.org/pypi/memcached_lock>`_
- `memcachelock <https://pypi.python.org/pypi/memcachelock>`_
- `unimr.memcachedlock <https://pypi.python.org/pypi/unimr.memcachedlock>`_
- `DistributedLock <https://pypi.python.org/pypi/DistributedLock>`_

- `distributing-locking-python-and-redis <https://chris-lamb.co.uk/posts/distributing-locking-python-and-redis>`_
- `mpessas/python-redis-lock <https://github.com/mpessas/python-redis-lock/blob/master/redislock/lock.py>`_
- `pylock <https://pypi.python.org/pypi/pylock>`_
- `python-redis-lock <https://pypi.python.org/pypi/python-redis-lock>`_
- `redis-py <https://github.com/andymccurdy/redis-py/blob/master/redis/lock.py>`_
- `redlock <https://pypi.python.org/pypi/redlock>`_
- `retools <https://github.com/bbangert/retools/blob/master/retools/lock.py>`_
- `score.distlock <https://pypi.python.org/pypi/score.distlock>`_


.. _cache-dependencies: https://bitbucket.org/emacsway/cache-dependencies

.. _Coupling: http://wiki.c2.com/?CouplingAndCohesion
.. _Cohesion: http://wiki.c2.com/?CouplingAndCohesion
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
.. _Coarse-Grained Lock: http://martinfowler.com/eaaCatalog/coarseGrainedLock.html
.. _Identity Map: http://martinfowler.com/eaaCatalog/identityMap.html
.. _DataMapper: http://martinfowler.com/eaaCatalog/dataMapper.html
.. _Pessimistic Offline Lock: http://martinfowler.com/eaaCatalog/pessimisticOfflineLock.html
.. _Unit of Work: http://martinfowler.com/eaaCatalog/unitOfWork.html

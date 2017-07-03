
About problems of cache invalidation. Cache tagging.
====================================================


.. post:: May 21, 2016
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

I've chosen the second option.


Tagging of nested caches
========================

Because tags are verified at the moment of cache reading, let's imagine, what happens, when one cache will be nested to other cache.
Multi-level cache is not so rarely.
In this case, the tags of inner cache will never be verified, and outer cache will alive with outdated data.
At the moment of creation the outer cache, it must accept the all tags from the inner cache into own tag list.
If we pass the tags from the inner cache to the outer cache in an explicit way, it violates encapsulation!
So, cache system must keep track the relations between all nested caches, and pass automatically all tags from an inner cache to its outer cache.


Replication problem
===================

When tag has been invalidated, a concurrent thread/process can recreate a dependent cache with outdated data from slave, before slave will be updated.

The best solution of this problem is a :ref:`locking the tag <tags-lock-en>` for cache creation until slave will be updated.
But, first, this implies a certain overhead, and secondly, all threads (including current one) continue to read stale data from the slave (unless reading from master specified explicitly).

A compromise solution can be simple re-invalidation of the tag after period of time when the slave is guaranteed to be updated.

I saw also an approach of cache regeneration instead of removing/invalidation.
This approach entail ineffective memory usage (in case LRU_ principle).
Also, this approach does not resolve the problem of complexity of invalidation logic.
Usually, this approach is the cause of a lot of bugs.
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

Then the process P2 has begun the transaction, updated data in the DB, invalidated tag T1, and ascuired the lock for the tag T1 until the transaction will be committed.

Process P1 are trying to read the cache with key C1, which is tagged by the tag T1, and is not valid anymore.
Not being able to read the invalid cache C1, the process P1 receives the outdated data from the DB (remember, the transaction isolation level is "Repeatable read").
Then the process P1 are trying to create the cache C1, and waiting while the tag T1 will be released.

When the transaction of process P2 is committed, the process P2 releases the tag T1.
Then the process P1 writes the outdated data into the cache C1.
This locking does not make sense.

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

There is the 3 main reasons:

- The quickness of response is important for web-application, otherwise a client simply can not wait for the response.
- There is no any reason to wait for lock release longer than it takes time to create the cache itself.
- An increase in the number of pending processes can lead to a memory overflow, or reaching of available workers of the server, or reaching of the maximum allowed number of connections to the database or other resources.

Also, there would be a problem with the implementation, since it is impossible to correctly block all tags by single query.

- First, we have to use method ``cache.add()`` instead of ``cache.set_many()`` for locking, to ensure the atomicity of the existence check and cache creation.
- Second, each tag should be locked by separate query, that increases the overhead.
- Third, the locking by single query per tag can lead to Deadlock_, the probability of which can be significantly reduced by topological sorting.

We should also mention the possibility of `row-level locking by DB <https://www.postgresql.org/docs/9.5/static/explicit-locking.html>`__ using `SELECT FOR UPDATE <https://www.postgresql.org/docs/9.5/static/sql-select.html#SQL-FOR-UPDATE-SHARE>`_. But it works only when both transactions use `SELECT FOR UPDATE`_, otherwise `it does not work <https://www.postgresql.org/docs/9.5/static/transaction-iso.html#XACT-READ-COMMITTED>`__:

    When a transaction uses this isolation level, a SELECT query (without a FOR UPDATE/SHARE clause) sees only data committed before the query began; it never sees either uncommitted data or changes committed during query execution by concurrent transactions. In effect, a SELECT query sees a snapshot of the database as of the instant the query begins to run.

But no one uses cache of select for update (it doesn't make sense to do it, and usually select for update is not used by web-applications because business transaction is used instead). Also, this approach is not able to solve the problem of replication.


.. _thundering-herd-en:

Thundering herd
===============

But what we can to do if cached logic is really resource intensive?

Dogpile is also known as `Thundering Herd`_ effect or cache stampede.

The answer is simple - Pessimistic Lock. But we have to lock not tags, but the key of the cache (or group of related keys, see `Coarse-Grained Lock`_, especially when using aggregate queries).
It's because of when the cache key is released, the cache must be guaranteed to be created (but tags has many-to-many relation to caches).

The lock must cover the entire code fragment from reading the cache to creating it.
And this responsibility is not related to invalidation.

There is a lot of libraries which solve the issue, for example:

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


Transaction problem
===================

When web-application has good traffic, it's possible the concurrent process recreates the cache with the outdated data since the tag has been invalidated but before the transaction is committed.
In contrast to replication problem, here is the manifestation of the problem strongly depends on the quality of the ORM, and the probability of problems is reduced when you use a pattern `Unit of Work`_.

Let to consider the problem for each transaction isolation level <Isolation_>`_ separately.


Read uncommitted
----------------

Тут все просто, и никакой проблемы не может быть в принципе. В случае использования репликации достаточно сделать отложенный повтор инвалидации через интервал времени гарантированного обновления slave.


Read committed
--------------

Тут уже проблема может присутствовать, особенно если Вы используете `ActiveRecord`_.
Использование паттерна `DataMapper`_ в сочетании с `Unit of Work`_ заметно снижает интервал времени между сохранением данных и фиксацией транзакции, но вероятность проблемы все равно остается.

В отличии от проблемы репликации, здесь предпочтительней было бы блокирование создания кэша до момента фиксации транзакции, так как текущий поток видит в БД не те данные, которые видят параллельные потоки.
А поскольку нельзя гарантированно сказать какой именно поток, текущий или параллельный, создаст новый кэш, то создание кэша до фиксации транзакции было бы желательно избежать.

Тем не менее, этот уровень изоляции не является достаточно серьезным, и выбирается, как правило, для повышения степени параллелизма, т.е. с той же целью что и репликация.
А в таком случае, эта проблема обычно поглощается проблемой репликации, ведь чтение делается все равно из slave.

Поэтому, дорогостоящая блокировка может быть компромисно заменена повторной инвалидацией в момент фиксации транзакции.


Repeatable read
---------------

Этот случай наиболее интересен.
Здесь уже без блокировки создания кэша не обойтись, хотя бы потому, что нам нужно знать не только список меток, но и время фиксации транзакции, которая осуществила инвалидацию метки кэша.

Мало того, что мы должны заблокировать метку с момента инвалидации до момента фиксации транзакции, так мы еще и не можем создавать кэш в тех параллельных транзакциях, которые были открыты до момента фиксации текущей транзакции.

Хорошая новость заключается в том, что раз уж мы и вынуждены мириться с накладными расходами на блокировку меток, то можно блокировать их вплоть до обновления slave, и обойтись без компромисов.


Serializable
------------

Поскольку несуществующие объекты обычно не кэшируются, то здесь достаточно ограничится той же проблематикой, что и для уровня `Repeatable read`_.


Множественные соединения с БД
=============================

Если Вы используете разные БД, и их транзакции синхронны, или просто используется репликация, Вы можете использовать по одному экземляру внешнего кэша (враппера) для каждого экземпляра внутреннего кэша (бэкенда).
Транзакции кэша не обязаны строго соответствовать системным транзакциям каждой БД.
Достаточно того, чтобы они выполняли свое предназначение, - не допускать подмену данных посредством кэша в параллельных потоках.
Поэтому, они могут охватывать несколько системных транзакций БД.

Но если Вы используете несколько соединений к одной и той же БД (что само по себе странно, но теоретически могут быть случаи когда нет возможности расшарить коннект для нескольких ORM в едином проекте), или же просто транзакции различных БД не синхронны, то Вы можете сконфигурировать внешний кэш так, чтобы иметь по одному экземпляру внешнего кэша на каждое соединение с БД для каждого экземпляра внутреннего кэша.


Динамические окна в кэше
========================

Есть два взаимно-дополняющих паттерна, основанных на диаметрально противоположных принципах, - `Decorator`_ и `Strategy`_.
В первом случае изменяемая логика располагается вокруг объявленного кода, во втором - передается внутрь него.
Обычное кэширование имеет черты паттерна `Decorator`_, когда динамический код расположен вокруг закэшированной логики.
Но иногда в кэше небольшой фрагмент логики не должен подлежать кэшированию.
Например, персонализированные данные пользователя, проверка прав и т.п.

Один из вариантов решения этой проблемы - это использование технологии `Server Side Includes`_.

Другой вариант - это использование двухфазной шаблонизации, например, используя библиотеку `django-phased <https://pypi.python.org/pypi/django-phased>`_.
Справедливости ради нужно отметить, что решение имеет немаленькое ресурсопотребление, и в некоторых случаях может нивелировать (если не усугублять) эффект от кэширования.
Возможно, именно поэтому, оно не получило широкого распространения.

Популярный шаблонный движок Smarty на PHP имеет функцию `{nocache} <http://www.smarty.net/docs/en/language.function.nocache.tpl>`_.

Но более интересной мне показалась возможность использовать в качестве динамического окна обычный Python-код, и абстрагироваться от сторонних технологий.


.. update:: Nov 06, 2016

    Добавлен абстрактный менеджер зависимостей.


Абстрактный менеджер зависимостей
=================================

Долгое время мне не нравилось то, что о логике, ответственной за обработку тегов, были осведомлены сразу несколько различных классов с различными обязанностями.

Было желание инкапсулировать эту обязанность в отдельном `классе-стратегии <Strategy_>`_, как это сделано, например, в `TagDependency of YII framework`_,
но не хотелось ради этого увеличивать накладные расходы в виде `дополнительного запроса на каждый ключ кэша для сверки его меток <https://github.com/yiisoft/yii2/blob/32f4dc8997500f05ac3f62f0505c0170d7e58aed/framework/caching/Cache.php#L187>`_, что означало бы лишение метода ``cache.get_many()`` своего смысла - агрегирования запросов.
По моему мнению, накладные расходы не должны превышать одного запроса в совокупности на каждое действие, даже если это действие агрегированное, такое как ``cache.get_many()``.

Кроме того, у меня там был еще один метод со спутанными обязанностями для обеспечения возможности агрегации запросов в хранилище, что большого восторга не вызывало.

Но мысль инкапсулировать управление тегами в отдельном абстрактном классе, отвечающем за управления зависимостями, и получить возможность использовать для управления инвалидацией не только теги, но и любой иной принцип, включая компоновку различных принципов, мне нравилась.

Решение появилось с введение класса `Deferred <https://bitbucket.org/emacsway/cache-dependencies/src/default/cache_tagging/defer.py>`_.
Собственно это не Deferred в чистом виде, в каком его привыкли видеть в асинхронном программировании, иначе я просто использовал бы эту `элегантную и легковесную библиотечку <https://pypi.python.org/pypi/defer>`_, любезно предоставленную ребятами из Canonical.

В моем же случае, требуется не только отложить выполнение задачи, но и накапливать их с целью агрегации однотипных задач, которые допускают возможность агрегации (``cache.get_many()`` является как раз таким случаем).

Возможно, название Queue или Aggregator здесь подошло бы лучше, но так как с точки зрения интерфейса мы всего лишь откладываем выполнение задачи, не вникая в детали ее реализации, то я предпочел оставить название Deferred.

Все это позволило выделить интерфейс абстрактного класса, ответственного за управление зависимостями, и теперь управление метками кэша стало всего лишь одной из его возможных реализаций в виде класса `TagsDependency <https://bitbucket.org/emacsway/cache-dependencies/src/default/cache_tagging/dependencies.py>`_.

Это открывает перспективы создания других вариантов реализаций управления зависимостями, например, на основе наблюдения за изменением какого-либо файла, или SQL-запроса, или какого-то системного события.


Gratitude
=========

Thanks a lot to `@akorn <https://bitbucket.org/akorn>`_ for the meaningful discussion of the problem of caching.


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

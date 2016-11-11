
About problems of cache invalidation. Cache tagging.
====================================================


.. post::
   :language: en
   :tags: cache
   :category:
   :author: Ivan Zakrevsky

About my experience of solving problems in cache invalidation, and about principles of the library `cache-tagging`_.

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
This approach entail ineffective memory usage (in case LRU principle).
К тому же, он не решает проблему сложности инвалидации и по сути мало чем отличается от обычного удаления кэша, возлагая всю сложность на само приложение.
Так же он таит множество потенциальных баг.
Например, он чувствителен к качеству ORM, и если ORM не приводит все атрибуты инстанции модели к нужному типу при сохранении, то в кэш записываются неверные типы данных.
Мне приходилось видеть случай, когда атрибут даты записывался к кэш в формате строки, в таком же виде, в каком он пришел от клиента.
Хотя он и записывался в БД корректно, но модель не делала приведение типов без дополнительных манипуляций при сохранении (семантическое сопряжение).


Проблема репликации
===================

При инвалидации кэша параллельный поток может успеть воссоздать кэш с устаревшими данными, прочитанными из slave в перид времени после инвалидации кэша, но до момента обновления slave.

Лучшим решением было бы :ref:`блокирование создания кэша <tags-lock-en>` до момента обновления slave.
Но, во-первых, это сопряжено с определенными накладными расходами, а во-вторых, все потоки (в том числе и текущий) продолжают считывать устаревшие данные из slave (если не указано явное чтение из мастера).
Поэтому, компромиссным решением может быть просто повторная инвалидация кэша через период времени гарантированного обновления slave.

В своей практике мне приходилось встречать такой подход как регенерация кэша вместо его удаления/инвалидации.
Такой подход влечет за собой не совсем эффективное использование памяти кэша (работающего по LRU-принципу).
К тому же, он не решает проблему сложности инвалидации, и, в данном вопросе, мало чем отличается от обычного удаления кэша по его ключу, возлагая всю сложность на само приложение.
Так же он таит множество потенциальных баг.
Например, он чувствителен к качеству ORM, и если ORM не приводит все атрибуты инстанции модели к нужному типу при сохранении, то в кэш записываются неверные типы данных.
Мне приходилось видеть случай, когда атрибут даты записывался к кэш в формате строки, в таком же виде, в каком он пришел от клиента.
Хотя он и записывался в БД корректно, но модель не делала приведение типов без дополнительных манипуляций при сохранении (семантическое сопряжение).


.. _tags-lock-en:

Реализация блокировки меток
===========================

**Блокировка меток** в библиотеке реализована в виде обхода параллельными потоками процедуры сохранения кэша, помеченного заблокированной меткой.

Почему не была использована пессимистическая блокировка меток (`Pessimistic Offline Lock`_), или `Mutual Exclusion`_?
Вопрос :ref:`резонный <thundering-herd-en>`, ведь закэшированная логика может быть достаточно ресурсоемкой.
При такой реализации параллельные потоки ожидали бы освобождения заблокированной метки.

Библиотека предназначена, прежде всего, для управления инвалидацией кэша.

Предположим, поток П1 начал транзакцию с уровнем изоляции Repeatable read.

Следом за ним, поток П2 начал транзакцию, изменил данные в БД, и вызвал инвалидацию метки М1, что наложило блокировку на метку М1 до момента фиксации транзакции.

Поток П1 пытается прочитать кэш К1, который прошит меткой М1, и является невалидным.
Не сумев прочитать невалидный кэш К1, поток П1 получает данные из БД, которые уже утратили актуальность (напомню, уровень изоляции - Repeatable read).
Затем он пытается создать кэш К1, и встает в ожидание, так как на метку К1 наложена пессимистическая блокировка.

Во время фиксации транзакции, поток П2 освобождает метку М1.
Затем поток П1 записывает в кэш устаревшие данные.
Смысла от такой блокировки нет.

Но что если мы будем проверять статус метки не во время создания кэша, а во время чтения кэша?
Изменило бы это хоть что-то?

Изменило бы. Во-первых, добавило бы оверхед на логику чтения.
Во-вторых, изменило бы результат, если бы уровень изоляции транзакции не превышал Read committed.
Для уровня изоляции Repeatable read (выбранный по умолчанию для ряда БД) и выше, - ничего не изменило бы.
Для этого пришлось бы блокировать поток еще до начала транзакции.

Таким образом, данное решение было бы половинчатым, не универсальным, и содержало бы неконтролируемую зависимость.
Для 2-х из 4-х уровней изоляции транзакций работать не будет.

Кроме конструктивного препятствия есть еще и другие.

Библиотека ориентирована главным образом на веб-приложения.
Ожидание параллельных потоков до момента окончания транзакции, или до момента обновления slave, который в некоторых случаях может длиться 8 секунд и более, практически не реализуемо в веб-приложениях.

Основных причин здесь три:

- Для веб-приложения важна быстрота отклика, так как клиент может просто не дождаться ответа.
- Нет смысла ожидать создание кэша более, чем требуется времени на само создание кэша.
- Рост количества ожидающих потоков может привести к перерасходу памяти, или доступных воркеров сервера, или исчерпанию максимально допустимого числа коннектов к БД или других ресурсов.

Так же возникла бы проблема с реализацией, так как корректно заблокировать все метки одним запросом невозможно.

- Во-первых, для блокировки метки нужно использовать метод ``cache.add()`` вместо ``cache.set_many()``, чтобы гарантировать атомарность проверки существования и создания кэша.
- Во-вторых, каждую метку нужно блокировать отдельным запросом, что увеличило бы накладные расходы.
- В-третьих, поодиночное блокирование чревато взаимной блокировкой (`Deadlock <https://en.wikipedia.org/wiki/Deadlock>`_), вероятность которой можно заметно сократить с помощью топологической сортировки.


.. _thundering-herd-en:

Thundering herd
===============

Но что делать, закэшированная логика действительно очень ресурсоемка?

Dogpile известен так же как `thundering herd <http://en.wikipedia.org/wiki/Thundering_herd_problem>`_ effect или cache stampede.

Ответ прост, - пессимистическая блокировка. Только не меток кэше, а ключа кэша.
Потому что при освобождении блокировки кэш должен быть гарантированно создан (а кэш и метки связаны отношением many to many).

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

Отдельно стоит упомянуть возможность `блокировки строк в БД <https://www.postgresql.org/docs/9.5/static/explicit-locking.html>`__ при использовании выражения `SELECT FOR UPDATE <https://www.postgresql.org/docs/9.5/static/sql-select.html#SQL-FOR-UPDATE-SHARE>`_. Но это будет работать только в том случае, если обе транзакции используют выражение `SELECT FOR UPDATE`_, в `противном случае <https://www.postgresql.org/docs/9.5/static/transaction-iso.html#XACT-READ-COMMITTED>`__:

    When a transaction uses this isolation level, a SELECT query (without a FOR UPDATE/SHARE clause) sees only data committed before the query began; it never sees either uncommitted data or changes committed during query execution by concurrent transactions. In effect, a SELECT query sees a snapshot of the database as of the instant the query begins to run.

Однако, выборку для модификации не имеет смысла кэшировать (да и вообще, в веб-приложениях ее мало кто использует, так как этот вопрос перекрывается уже вопросом организации бизнес-транзакций), соответственно, ее блокировка мало чем может быть полезна в этом вопросе. К тому же она не решает проблему репликации.



Проблема транзакций
===================

Если Ваш проект имеет более-менее нормальную посещаемость, то с момента инвалидации кэша и до момента фиксации транзакции, параллельный поток может успеть воссоздать кэш с устаревшими данными.
В отличии от проблемы репликации, здесь проявление проблемы сильно зависит от качества ОРМ, и вероятность проблемы снижается при использовании паттерна `Unit of Work`_.

Рассмотрим проблему для каждого `уровня изоляции транзакции <Isolation_>`_ по отдельности.


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


Динамические окна в кэше
========================

Есть два взаимно-дополняющих паттерна, основанных на диаметрально противоположных принципах, - `Decorator`_ и `Strategy`_.
В первом случае изменяемая логика располагается вокруг объявленного кода, во втором - передается внутрь него.
Обычное кэширование имеет черты паттерна `Decorator`_, когда динамический код расположен вокруг закэшированной логики.
Но иногда в кэше небольшой фрагмент логики не должен подлежать кэшированию.
Например, персонализированные данные пользователя, проверка прав и т.п.

Один из вариантов решения этой проблемы - это использование технологии `Server Side Includes <https://en.wikipedia.org/wiki/Server_Side_Includes>`_.

Другой вариант - это использование двухфазной шаблонизации, например, используя библиотеку `django-phased <https://pypi.python.org/pypi/django-phased>`_.
Справедливости ради нужно отметить, что решение имеет немаленькое ресурсопотребление, и в некоторых случаях может нивелировать (если не усугублять) эффект от кэширования.
Возможно, именно поэтому, оно не получило широкого распространения.

Популярный шаблонный движок Smarty на PHP имеет функцию `{nocache} <http://www.smarty.net/docs/en/language.function.nocache.tpl>`_.

Но более интересной мне показалась возможность использовать в качестве динамического окна обычный Python-код, и абстрагироваться от сторонних технологий.


Абстрактный менеджер зависимостей
=================================

Долгое время мне не нравилось то, что о логике, ответственной за обработку тегов, были осведомлены сразу несколько различных классов с различными обязанностями.

Было желание инкапсулировать эту обязанность в отдельном `классе-стратегии <Strategy_>`_, как это сделано, например, в `TagDependency of YII framework`_,
но не хотелось ради этого увеличивать накладные расходы в виде `дополнительного запроса на каждый ключ кэша для сверки его меток <https://github.com/yiisoft/yii2/blob/32f4dc8997500f05ac3f62f0505c0170d7e58aed/framework/caching/Cache.php#L187>`_, что означало бы лишение метода ``cache.get_many()`` своего смысла - агрегирования запросов.
По моему мнению, накладные расходы не должны превышать одного запроса в совокупности на каждое действие, даже если это действие агрегированное, такое как ``cache.get_many()``.

Кроме того, у меня там был еще один метод со спутанными обязанностями для обеспечения возможности агрегации запросов в хранилище, что большого восторга не вызывало.

Но мысль инкапсулировать управление тегами в отдельном абстрактном классе, отвечающем за управления зависимостями, и получить возможность использовать для управления инвалидацией не только теги, но и любой иной принцип, включая компоновку различных принципов, мне нравилась.

Решение появилось с введение класса `Deferred <https://bitbucket.org/emacsway/cache-tagging/src/default/cache_tagging/defer.py>`_.
Собственно это не Deferred в чистом виде, в каком его привыкли видеть в асинхронном программировании, иначе я просто использовал бы эту `элегантную и легковесную библиотечку <https://pypi.python.org/pypi/defer>`_, любезно предоставленную ребятами из Canonical.

В моем же случае, требуется не только отложить выполнение задачи, но и накапливать их с целью агрегации однотипных задач, которые допускают возможность агрегации (``cache.get_many()`` является как раз таким случаем).

Возможно, название Queue или Aggregator здесь подошло бы лучше, но так как с точки зрения интерфейса мы всего лишь откладываем выполнение задачи, не вникая в детали ее реализации, то я предпочел оставить название Deferred.

Все это позволило выделить интерфейс абстрактного класса, ответственного за управление зависимостями, и теперь управление метками кэша стало всего лишь одной из его возможных реализаций в виде класса `TagsDependency <https://bitbucket.org/emacsway/cache-tagging/src/default/cache_tagging/dependencies.py>`_.

Это открывает перспективы создания других вариантов реализаций управления зависимостями, например, на основе наблюдения за изменением какого-либо файла, или SQL-запроса, или какого-то системного события.


Заключение
==========

Надо признать, что я уделяю этой библиотеке мало внимания (а писалась она еще на заре моего освоения языка Python), и многое из того, что хотелось бы сделать, там не сделано.


Благодарности
=============

Выражаю благодарность `@akorn <https://bitbucket.org/akorn>`_ за содержательное обсуждение проблематики кэширования.


.. _cache-tagging: https://bitbucket.org/emacsway/cache-tagging

.. _Decorator: https://en.wikipedia.org/wiki/Decorator_pattern
.. _Isolation: https://en.wikipedia.org/wiki/Isolation_(database_systems)
.. _Mutual Exclusion: https://en.wikipedia.org/wiki/Mutual_exclusion
.. _Observer: https://en.wikipedia.org/wiki/Observer_pattern
.. _Strategy: https://en.wikipedia.org/wiki/Strategy_pattern

.. _ActiveRecord: http://www.martinfowler.com/eaaCatalog/activeRecord.html
.. _DataMapper: http://martinfowler.com/eaaCatalog/dataMapper.html
.. _Pessimistic Offline Lock: http://martinfowler.com/eaaCatalog/pessimisticOfflineLock.html
.. _Unit of Work: http://martinfowler.com/eaaCatalog/unitOfWork.html

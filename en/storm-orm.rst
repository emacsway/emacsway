
.. post::
   :language: en
   :tags: ORM, Storm ORM, DataMapper, DB, SQL, Python
   :category:
   :author: Ivan Zakrevsky


Why I prefer Storm ORM
======================

For enterprise aplications I began to use `KISS-style`_ `Storm ORM`_, let me explaine why.

.. contents:: Contents


.. _orm-criteria-en:

My requirements for ORM
=======================

\- **Quickness**. ORM should be fast.
ORM should to have `Identity Map`_ to prevent duplicated queries to DB if the object is already loaded to the memory.
This is important when several isolated scopes are trying to load the same object to the own namespace.
Also, I think, `Identity Map`_ should be configurable for different transaction isolation levels, for example, to prevent query to DB when object does not exist and transaction isolation level is "Serializable".

\- **Simplicity**. ORM should not scare you from debugger, you have to understand what it does by browsing the source code.
Any product sooner or later can be dead, or author can lose an interest in it, thus you should be able to support the product yourself.
New developers of a team should be able to master the ORM quickly.
And the only source of truth about the code is the code itself.
Documentation and comments is good, but they are not always comprehensive and actual.
And often the product should be adapted, extended for your requirements.
Thus, simplicity is important.

\- **Architecture**. Proper separation of levels of abstraction, adherence to the basic principles of architecture (such as `SOLID`_).

If you are not able to use some component of the ORM separately, for example SQLBuilder, then, probably, it would be better to use raw pattern DataMapper_ instead of the ORM.
Well designed ORM allows you to use its components separately, such as `Query Object`_ (SQLBuilder), Connection, `DataMapper`_, `Identity Map`_, `Unit of Work`_, `Repository`_.
Does the ORM allow you to use Raw-SQL (entirely or partially)?
Are you able to use only DataMapper (without Connection, SQLBuilder etc.)?
Are you able to substitute the DataMapper by `Service Stub`_, to be free from DB for testing?

The possibilities of any ORM have to be expanded.
Are you able to extend your ORM without monkey-patching, forks, patches?
Does the ORM follow to the `Open/Closed Principle`_ (OCP)?

    "The primary occasion for using Data Mapper is when you want the database schema and the object model to evolve independently. The most common case for this is with a Domain Model (116). Data Mapper's primary benefit is that when working on the domain model you can ignore the database, both in design and in the build and testing process. The domain objects have no idea what the database structure is, because all the correspondence is done by the mappers."
    («Patterns of Enterprise Application Architecture» [#fnpoeaa]_)

\- `ACID`_. Good ORM takes care of that the object has always been consistent to the record of the DB.

Suppose, you have loaded the object to the memory, and then executed transaction commit.
The object has a lot of references to it, but the object has been updated by a concurrent process.
If you try to modify the object, the changes of the concurrent process will be lost.
When you are doing transaction commit, you have to synchronize the object to the record of the DB, and at the same time to keep alive all references to the object.
See also this `article <http://techspot.zzzeek.org/2012/11/14/pycon-canada-the-sqlalchemy-session-in-depth/>`__ and `presentation <http://techspot.zzzeek.org/files/2012/session.key.pdf>`__.
To ensure the integrity of data, the transaction support alone is not enough for the application.
Of course, this is not a critical requirement, but without it you can not completely hide the source of data in the code.

\- **Hiding the data source**. A good ORM allows you to forget about its existence, and handle instances of models as if they were ordinary objects.
It would not disclose the source of the data by requiring you to explicitly call the method to save the objects.
It would not oblige you to "reload" objects.
It makes it easy to replace the mapper, even if you change the relational database to non-relational.

Imagine that you have created two new objects, one of which refers to another with foreign key.
Can you create a link between them before at least one of them is stored in the database and received the primary key?
Will the value of the foreign key of the associated object be updated when the first object is saved and the primary key is received?

A good ORM prevents the deadlock, because it saves all objects just before the commit, minimizing the time interval from the first save to the commit.
Also it allows you to influence the order of saving objects, for example, using topological sorting to prevent the deadlock.


.. _storm-orm-advantages-en:

Advantages
==========

Despite the release number, the code is fairly stable.
Successful architecture in combination with the KISS_ principle creates a false illusion that the Storm ORM is allegedly not developing.
This is not true.
In fact, there's simply nothing to develop.
For three years of investigation of the source code of Storm ORM, I did not find anything that could be improved.
Storm ORM can be extended, but not improved.
`Commits occur regularly <https://code.launchpad.net/storm>`__.
But they can be described as "polishing".

Storm ORM supports composite keys and relations (after Django ORM I sighed with relief).

It allows you to express SQL queries of almost any complexity (at least constructively).

It works with any number of databases.

It implements `DataMapper`_ pattern, which means classes of models free of metadata and database access logic, as is typical for `ActiveRecord`_.
Model class can be inherited from the bare class `object`_.

Due to `Identity Map`_, `Storm ORM`_ is very fast.
On the page of one of the projects, after the introduction of Storm ORM (instead of Django ORM), the time consumption by ORM reduced from 0.21 seconds to 0.014 seconds (i.e. 15 times), and the total page generation time was reduced by half, from 0.48 seconds to 0.24 seconds.
The number of queries to the database reduced from 88 to 7.
Identity Map also makes utilities of the prefetch_related() type unnecessary, but only for foreign keys referencing the primary key.

It is very pleasant to work with the code Storm ORM.
Here you can find a lot of interesting techniques for code optimization.
We must pay tribute to the developers Storm ORM, - they made a real intellectual feat.
All the code is carefully thought out.
Any attempt to improve it usually only convince the correctness of existing solutions.

Storm ORM correctly processes transactions.
There can not be found thoughtless reconnect when connection is lost during an incomplete transaction.
The connection can be restored only if it can not affect the integrity of the data.
The transactions are implemented in two levels.
In the case of transaction rollback, the state of objects in the memory is also rolled back.

Storm ORM is able to compile a selection criteria to the collection of filters of Python-code, which can be applied to any collection of objects in the memory.
This feature allows you to create a dummy mapper for tests.
To select objects from ``Store()`` by primary key (even from a Foreign Key) you don't have to do anything, because due to `Identity Map`_ pattern you don't have to send objects to the database, thus you are able to use (partially) `Identity Map`_ as dummy mapper.

Storm ORM does not convert values immediately, at the time of loading the object.
Instead, it simply wraps the value in the wrapper (adapter) - the Variable class.

It allows you:

- Control the assignment and access policy.
- Optimize resource consumption (call-by-need lazy conversion which delays the conversion until its value is needed).
- Keep the initial value of each attribute, observe its changes, perform rollback at the object level.
- Watch for value changes (the observer) and update related objects.
- Synchronize the value of the object with the value of the database record.
- Implement "Defensive Programming" and prevent assignment of invalid value. You are not able to forget validation before to save anymore. This solves "G22: Make Logical Dependencies Physical" [#fncc]_ and "G31: Hidden Temporal Couplings" [#fncc]_.
- Validate the value only when assigning it from the outside, but not from the database. This eliminates the problem of the impossibility of re-saving the objects when validation rules are changed.
- Convert the value to the required representation, depending on the context of the usage (Python or DB).

The last one, however, has some nuances.

For example, we add a selection criterion::

    (GeoObjectModel.point == author_instance.location)

Converter of which attribute should be used here, ``GeoObjectModel.point`` or ``AuthorModel.location``?
Obviously ``AuthorModel.location`` because it provides value.
But here converter of ``GeoObjectModel.point`` will be used.
What happens if these converters have different behavior?
And what happens if we pass such a criterion: ``Func('SOME_FUNCTION_NAME', AuthorModel.location)``?

To be fair, Storm ORM made a major breakthrough in ordering the conversion issue, compared to most other ORMs, and created the right grounding to create the ideal conversion.
If you follow simple rules, converters will work perfectly correctly (to achieve this, you must pass the `Variable() instance  <http://bazaar.launchpad.net/~storm/storm/trunk/view/477/storm/store.py#L597>`__ to the selection criteria, i.e. wrapped value).
Many other ORMs do not have this technical capability at all, because they perform the conversion when the object is created.
In other words, the converters of other ORMs are actually tied to the type of values and not to a particular attribute (as declared), which makes them virtually useless, because this `responsibility already is imposed for the connector <http://initd.org/psycopg/docs/advanced.html#adapting-new-python-types-to-sql-syntax>`__.

Storm ORM does not impose you a way to obtain a connection.
You `can easily <http://bazaar.launchpad.net/~storm/storm/trunk/view/477/storm/database.py#L502>`__ share a connection between two ORMs or use `some special way <http://eventlet.net/doc/modules/db_pool.html>`__ of getting a connection.

Storm ORM `does not oblige <https://lists.ubuntu.com/archives/storm/2009-June/001010.html>`__ to declare a database schema in the code.
This corresponds to the `DRY`_ principle, since the schema already exists in the database.
Also, complete control of the database schema `can be achieved easier by the facilities of the database <https://blogs.gnome.org/jamesh/2007/09/28/orm-schema-generation/>`__.
Usually large projects, which use replication and sharding, use own tools to control the database schema.
You also able to use package `storm.schema <http://bazaar.launchpad.net/~storm/storm/trunk/files/477/storm/schema/>`__ which is the part of Storm ORM.
`Unlike to SQLAlchemy <http://docs.sqlalchemy.org/en/rel_1_1/core/reflection.html>`__, Storm ORM does not provide automatical loading of undeclared properties of model from the DB.
It can be implemented easily, but there is two points. First, you have to perform DB-query at the level of initialization of the code of module. Second, it's not enough anymore to browse source code to understand the schema of model.
Also, different types of Python can use the same data-type of DB, thus, DB schema is not enough to deplare model classes correctly.

Other advanteges you can see at the `Tutorial <https://storm.canonical.com/Tutorial>`__ and `Manual <https://storm.canonical.com/Manual>`__


.. _about-sqlalchemy-en:

About SQLAlchemy
================

Any `ORM could be good <http://aosabook.org/en/sqlalchemy.html>`__, if it `implements principles <http://techspot.zzzeek.org/2012/02/07/patterns-implemented-by-sqlalchemy/>`__ of popular book «Patterns of Enterprise Application Architecture» [#fnpoeaa]_.
Storm ORM contrasts with simplicity against the background of SQLAlchemy, just like VIM on the background of Emacs, or jQuery on the background of Dojo.
Ideologically, they have a lot in common, I would say that the Storm ORM is a simplified version of SQLAlchemy.
You would have studied the source code of Storm ORM much faster than introduction of tutorial of SQLAlchemy.
You can extend and adapt Storm ORM for your requirements much faster than you would have understood the way to implement it for SQLAlchemy.

But there is a border that makes SQLAlchemy more preferable than Storm ORM.
If the functionality of Storm ORM suits you, you "wield a pen", and have the time to adapt the library to your needs, then Storm ORM looks more attractive.
Otherwise, SQLAlchemy becomes preferable, even despite the level of complexity, because it provides a lot of solutions "out of the box".


.. _storm-orm-disadvantages-en:

Disadvantages
=============

Еhere were three cases in my practice, when I had to add to Storm ORM a few features, which already are implemented by SQLAlchemy (or its community).

1. `Bulk inserting of objects <http://docs.sqlalchemy.org/en/rel_1_1/orm/session_api.html#sqlalchemy.orm.session.Session.bulk_save_objects>`__, moreover, using the clause ON DUPLICATE KEY UPDATE.
2. Adaptation of `SQL Builder for interface of Django ORM <https://github.com/mitsuhiko/sqlalchemy-django-query>`__.
3. Support the pattern `Concrete Table Inheritance <http://docs.sqlalchemy.org/en/rel_1_1/orm/extensions/declarative/inheritance.html#concrete-table-inheritance>`__

Storm ORM `does not use thread locking <https://bugs.launchpad.net/storm/+bug/1412845>`__ for lazy modification of critical global metadata.
This is not a problem, and can be easily solved (enough to fulfill them immediately, under the lock).
But you have to know this, otherwise your server will have gone down for highly concurrent threads.

Most likely, you would have to extend Storm ORM.
The possibilities of SQL-builder should be extended.
Utils prefetch_related() for OneToMany() would be useful.
Probably, you may need to implement a cascade deletion using ORM, not a database.
And implement an object serializer.
Storm ORM does not implement the topological sort, but allows it to easily implement.

Class Store (which is the implementation of pattern Repository) combines also the responsibility of DataMapper_ and it's not so well.
For example, this creates a problem for implementing the pattern `Class Table Inheritance`_.
Storm ORM core developers advice `to replace Inheritance with Delegation <https://storm.canonical.com/Infoheritance>`__ (However, postgresql `supports inheritance <postgresql inheritance_>`__ itself (`DDL <postgresql inheritance DDL_>`__)).
The lack of a dedicated class for DataMapper forces you to clutter the domain model with `service logic <https://storm.canonical.com/Manual#A__storm_pre_flush__>`__.

.. Дескрипторы связей Storm ORM запрашивают store у объекта.
   Таким образом, если объект приаттачен к фиктивному стору, то и связи он будет искать в фиктивном сторе.
   Таким образом, дескрипторы не представляют никаких проблем для подмены реального стора на фиктивный.

.. По этим причинам мне захотелось сделать `ascetic ORM <https://bitbucket.org/emacsway/ascetic>`__ который был бы еще проще (который, впрочем, на сегодня является не более чем сборищем незавершенных мыслей).


.. _storm-orm-ambiguities-en:

About ambiguous
===============

ACID support has led to the fact that the domain model is not really pure.
The domain model has pure interface, behaves like realy plain object, and is inherited from the ``object`` class.
In fact, the instance of the model does not contain data, but refers to the data structure through descriptors.
It's a titanic work to implement it in the KISS style.
Although I'm not sure that the implementation of such a complex mechanism corresponds to the principle of KISS.
Perhaps, simplicity of implementation here would be preferable, rather than simplicity of the interface.
Nevertheless, it makes one argument against ORM less.

In addition, this solution does not provide full consistency of the behavior available for use.
Suppose you have created two new objects, the first of which refers to the second on the foreign key.
Then you created a link between them with a descriptor.
Before commit, you are able `to get the second object using the descriptor of the foreign key of the first object <https://storm.canonical.com/Tutorial#References_and_subclassing>`__.
But you aren't able to get the second objet by using the repository (i.e. class Store).
When you do commit, the both objects receive primary keys, and the value of the foreign key are automatically updated.
From now on you can get the second object by the repository.


.. _storm-orm-faq-en:

FAQ
===

*q: Storm ORM does not support Python3.*

a: If you migrated at least one library in Python3, then you understand that this process does not cause major difficulties.
The command ``2to3`` does 95% of work.
The only significant problem is the migration of the C-expansion.
Storm ORM is fast enough even without the C-expansion, and does not lose much in performance.
You can find the C-expansion for Python3 `here <http://bazaar.launchpad.net/~martin-v/storm/storm3k/view/head:/storm/cextensions.c>`__ (`diff <http://bazaar.launchpad.net/~martin-v/storm/storm3k/revision/438>`__)


*q: How t use Storm ORM with partial Raw-SQL*

a: It's better to avoid to do it, and extend the SQL-builder. But if you really need::

    >>> from storm.expr import SQL
    >>> from authors.models import Author
    >>> store = get_my_store()
    >>> list(store.find(Author, SQL("auth_user.id = %s", (1,), Author)))
    [<authors.models.Author object at 0x7fcd64cea750>]


*q: In which way I can use Storm ORM with a fully Raw-SQL, to get the result of query with instances of the models?*

A: Since Storm ORM uses the Data Mapper, Identity Map and Unit of Work patterns, you have to specify all the model fields in the query, and use the method ``Store._load_object()``::

    >>> store = get_my_store()
    >>> from storm.info import get_cls_info
    >>> from authors.models import Author

    >>> author_info = get_cls_info(Author)

    >>> # Load single object
    >>> result = store.execute("SELECT " + store._connection.compile(author_info.columns) + " FROM author where id = %s", (1,))
    >>> store._load_object(author_info, result, result.get_one())
    <authors.models.Author at 0x7fcc76a85090>

    >>> # Load collection of objects
    >>> result = store.execute("SELECT " + store._connection.compile(author_info.columns) + " FROM author where id IN (%s, %s)", (1, 2))
    >>> [store._load_object(author_info, result, row) for row in result.get_all()]
    [<authors.models.Author at 0x7fcc76a85090>,
     <authors.models.Author at 0x7fcc76a854d0>]


.. _why-orm-en:

Do you really need ORM?
=======================

Honestly, there is no need to use ORM always and everywhere.
In many cases (for example, if an application simply needs to issue a list of JSON values), the simplest `Table Data Gateway`_ is enough, which returns the list of simplest `Data Transfer Object`_.
This is an issue of personal preferences.


.. _why-query-object-en:

Do you really need Query Object?
--------------------------------

The only thing I'm absolutely sure of is that it's difficult do without without the `Query Object`_ pattern (which is also named as SQLBuilder), or rather impossible.

\1. Even the most staunch adherents of the "pure SQL" concept quickly encounter the inability to express the SQL query in its pure form, and are forced to dynamically compose it depending on the conditions.
And this is already a kind of SQLBuilder concept, albeit in a primitive form, and implemented in a particular way.
But particular solutions always take a lot of place, as they depart from the `DRY`_ principle.

Let me to illustrate it with an example.
Imagine a query to select ads from the database by 5 criteria.
You need to allow users to select the ads using a set of any number of the following criteria:

0. Without criteria.
1. By ad type.
2. By country, region, city.
3. By categories, including nested categories.
4. By users (all ads of the same user)
5. By search words.

Altogether, you would have to prepare 2 ^ 5 = 32 fixed SQL-requests, and this if you do not take into account the nestings of tree structures (otherwise 3-d criterion would have to be divided into 3 more criteria, as often the data is stored denormalized).

The list of possible combinations of criteria::

    0
    1
    1,2
    1,2,3
    1,2,3,4
    1,2,3,4,5
    1,2,4
    1,2,4,5
    1,2,5
    1,3
    1,3,4
    1,3,4,5
    1,3,5
    1,4
    1,4,5
    1,5
    2,
    2,3
    2,3,4
    2,3,4,5
    2,3,5
    2,4
    2,4,5
    2,5
    3
    3,4
    3,4,5
    3,5
    4
    4,5
    5

And if we add another criterion, it will be 2^6=64 combinations, i.e. in 2 times more.
One more, it will be 2^7=128 combinations.

128 fixed queries forced to abandon the concept of "pure SQL" in favor of the concept of "dynamic building of SQL-query."
The method that creates this query will take a lot of arguments, and this will affect the cleanness of the code.
You can divide the method by responsibilities, so that each method builds its part of the query.
But firstly, this approach will create the SQL-builder in a particular way (violation of the `DRY`_ principle).
And secondly, if you continue to clean up the methods, to free its from dependencies, and increase the `Cohesion`_ classes, then you will eventually come to the Criteria classes and implement the `Query Object`_ pattern.
Again, attempts to break this method will lead to a reduction in `Cohesion`_ of the class.
To restore the `Cohesion`_, you have to extract Criteria classes.

In other words, you will actually create an SQL-builder that can be extracted to a separate library, which can be evolved independently.

But what happens if you do not "clean up" the methods, release them from dependencies and increase the `Cohesion`_ of classes? You will get an unreadable messian with a lot of SQL pieces scattered across different methods.
Sometimes such "pieces" are made in the form of static methods of the class, which acquires the signs "G18: Inappropriate Static" [#fncc]_, and according to the recommendations of Robert C. Martin, there should be extracted the polymorphic object `Criteria`_.
In any case, the readability of such "pure SQL" (and this is one of the most weighty arguments in its favor) will be lost (it will be even lower than the readability of the query created by SQL-builder).

SQL-builders exists only because they are maximally implement the principle of `Single responsibility principle`_ (SRP).
In the "Chapter 10: Classes. Organizing for Change" of the widely known book «Clean Code: A Handbook of Agile Software Craftsmanship» [#fncc]_, C.Martin demonstrates the achievement of the `SRP`_ principle in the example of SQL-builder.

Similar to hybrid object, that contains disadvantages of data structures and objects, SQL-builder implemented in particular way contains disadvantages of both concepts.
They do not have the readability of Raw-SQL, nor the convenience of complete SQL-builders.
This forces us to abandon the dynamic construction, in favor of readability of the code, or to bring the levels of abstraction to a complete SQL-builder.

Also, the concept of "pure SQL" is not feasible in the implementation of the following patterns and approaches:

- Dynamically change the sorting
- Multilanguage implemented with suffixed columns
- `Concrete Table Inheritance`_
- `Class Table Inheritance`_
- `Entity Attribute Value`_
- etc.

\2. Такие запросы невозможно наследовать без `синтаксического анализа <https://pypi.python.org/pypi/sqlparse>`__ (например, чтобы просто изменить сортировку), что обычно влечет за собой их полное копирование.
А каждую копию приходится сопровождать отдельно, что усложняет сопровождение такого кода.
Впрочем, на досуге я написал простейший `mini-builder, который представляет SQL-запрос в виде многоуровневого списка с фрагментами Raw-SQL <http://sqlbuilder.readthedocs.io/en/latest/#short-manual-for-sqlbuilder-mini>`__, что позволяет полноценно выстраивать условно-составные SQL-запросы и при этом практически полностью сохраняет читаемость Raw-SQL.

\3. Мне нередко приходилось видеть среди файлов с Raw-SQL диффы на несколько сотен строк только потому, что в модель был добавлен новый атрибут, что имеет признаки "Divergent Change" [#fnr]_ и "Shotgun Surgery" [#fnr]_.
Это потому, что SQL-запросы содержат много дубликатов выражений.
SQL-код, даже если он в Python-файлах, все равно остается кодом.
И к нему так же справедливо правило "G5: Duplication" [#fncc]_ ("Duplicated Code" [#fnr]_).
В случае использования SQLBuilder таких проблем не возникает, так как необходимые метаданные для построения запроса (в частности, список выбираемых полей) хранятся в едином месте.

\4. При использовании концепции "чистого SQL", критерии выборки обычно передаются  в методы выборки в виде аргументов, из-за чего нередко приходится изменять их интерфейсы (а так же добавлять новые методы), когда добавляются новые поля данных и критерии выборки к ним, что нарушает `Open/Closed Principle`_ и имеет признаки "Divergent Change" [#fnr]_ и "Shotgun Surgery" [#fnr]_.

Напрашиватеся "`Introduce Parameter Object`_" [#fnr]_ с выделением класса Criteria паттерна `Query Object`_.
Этот подход исключит подобные проблемы, поскольку все критерии выборки инкапсулированы в единственном объекте (`Composite pattern`_), а так же освободит методы выборки от условных операторов "`Replace Conditional with Polymorphism`_" [#fnr]_.

В своем воображении (и в программном коде) человек оперирует объектами.
Способ сортировки и ее направление - характеризуют состояние объекта.
Критерии выборки - это тоже объекты, от которых мы ожидаем определенного поведения (образовывать композиции, влиять на выборку БД).
Когда объекты есть, но они не выражены в коде, программа теряет способность выражать замысел разработчика ("G16: Obscured Intent" [#fncc]_).

\5. Если какое-то значение объекта требует особой конвертации в DB представление, - нам придется загромождать код явным вызовом этих конвертаций.

\6. Существует тенденция (которая мне регулярно встречается) использования паттерна `Repository`_ в сочетании с Raw-SQL.
Поскольку сам Repository предназначен для сокрытия источника данных, то непонятно, как передавать в Repository критерии выборки, чтобы они были полностью абстрактны от источника данных, т.е. абстрактны от Raw-SQL.

В примитивных случаях, это, конечно, не проблема (можно передавать их именованными аргументами функции, хотя это, в свою очередь, вызывает проблемы описанные в п.4).

Но если требуется хотя бы пять нефиксированных, взаимозависимых или составных критериев (сочетающих вложенные приоритизированные операции "OR", "AND", логический "XOR" и др.), то это уже проблема, решение которой и входит в обязанности паттерна Query Object.
Передача же фрагментов SQL строк в качестве аргументов функции имеет признаки "G6: Code at Wrong Level of Abstraction" [#fncc]_ и  "G34: Functions Should Descend Only One Level of Abstraction" [#fncc]_.

\7. Нередко для условного составления запроса используется форматирование строк. Проблема в том, что тот объект, который хочет использовать этот запрос в модифицированной форме, должен быть осведомлен о деталях реализации механизма его модификации.
Возникает логическая зависимость, нарушается инкапсуляция.

Чтобы этого избежать, обычно объект, форматирующий запрос, наделяется методами, которые модифицируют запрос под потребности использующих его объектов.
Получается Божественный Объект, который должен знать о потребностях всех объектов, которые потенциально могут его использовать.

Это нарушает OCP и приводит к "Divergent Change" [#fnr]_ и "Shotgun Surgery" [#fnr]_. Нередко остается мусор в виде невостребованных методов, после удаления использующих их объектов.
Очень большие классы обычно разбиваются наследованием или композицией.
Это приводит к тому, что получить целостное представление о том, что делает метод, невозможно без неоднократного прерывания взгляда на изучение содержимого различных методов, классов, а то и файлов.

Паттерн Query Object предоставляет унифицированный интерфейс модификации запроса, освобождая объект запроса от необходимости знать о потребностях окружающих объектов.

\8. Отдельно хочу затронуть вопрос использвания синтаксических конструкций языка для построения SQL-запросов.
Я скажу, возможно, субъективно, но мне больше нравится использовать для этого объекты.
Более того, мне нравится когда сами синтаксические конструкции языка представлены объектами, как в Smalltalk.


.. _why-datamapper-en:

Нужен ли сам DataMapper?
------------------------

Что же касается самого маппера, то тут следует решить, нужна ли приложению `Domain Model`_, или вполне устроит паттерн `Transaction Script`_.
Я не буду останавливаться на этом выборе, так как он хорошо освещен в «Patterns of Enterprise Application Architecture» [#fnpoeaa]_.
Но если нуждам приложения больше соответствует Domain Model, то без полноценного ORM (пусть и самодельного) обойтись будет непросто, по крайней мере, для качественной, удобной и быстрой работы.

По поводу распространенных аргументов против ORM.
Я не буду затрагивать уже пронафталиненные темы вроде того, что базы данных не поддерживают наследования.
Во-первых, `поддерживают <postgresql inheritance_>`__ (`DDL <postgresql inheritance DDL_>`__).
Во-вторых, наследование можно заменить композицией. Кстати, полезность наследования в ООП до сих пор является `обсуждаемым вопросом <http://www.javaworld.com/article/2073649/core-java/why-extends-is-evil.html>`__. В Go-lang наследование отсутствует в пользу композиции.
Сами языки программирования реализуют наследование посредством композиции.
В-третьих, сегодня только ленивый не знает о паттернах
`Single Table Inheritance`_,
`Concrete Table Inheritance`_,
`Class Table Inheritance`_ и
`Entity Attribute Value`_.

Поэтому я затрону только два существенных на мой взгляд вопроса:

1. Представлять данные в памяти объектами, или структурами данных?
2. ACID, согласованность объекта в памяти и его данными на диске.

По поводу первого вопроса у меня нет однозначного мнения.
Мы живем в мире объектов, и именно поэтому появилось объектно-ориентированное программирование.
Человеку проще мыслить объектами.
В Python даже элементарные типы являются полноценными объектами, с методами, наследованием и т.п.

В чем отличие между структурой данных и объектом? В Python это отличие сугубо условное.
Объекты используют представление данных на абстрактном уровне.

    "Objects hide their data behind abstractions and expose functions that operate on that data. Data structure expose their data and have no meaningful functions."
    («Clean Code: A Handbook of Agile Software Craftsmanship» [#fncc]_)

Тут мы снова упираемся в вопрос Domain Model vs Transaction Script, поскольку доменная модель по своему определению охватывает поведение (функции) и свойства (данные).

Но есть еще один немаловажный момент.
Допустим, мы храним в БД две колонки - цена и валюта.
Или, например, данные полиморфной связи - тип объекта и его идентификатор.
Или координаты - x и y.
Или путь древовидной структуры - страна, область, город, улица.
Т.е. несколько данных образуют единую сущность, и изменение части этих данных не имеет никакого смысла.
Как задать политику доступа данных и гарантировать атомарность их изменения (кроме как использованием объектов или неизменяемых типов)?

Я думаю, что мы должны думать прежде всего о бизнес-задачах.
О том, какими объектами и как должна оперировать программа.
Вопросы реализации не должны диктовать бизнес-логику.
Вопросы хранения информации должны удовлетворять нашим требованиям, а не указывать нам требования.
Если бы это было не так, то объектно-ориентированное программирование до сих пор не возникло бы.

    "The whole point of objects is that they are a technique to package data with the processes used
    on that data. A classic smell is a method that seems more interested in a class other than the one
    it actually is in. The most common focus of the envy is the data."
    («Refactoring: Improving the Design of Existing Code» [#fnr]_)    

..

    "Now this design has some problems. Most important, the details of the table structure have leaked
    into the DOMAIN LAYER ; they should be isolated in a mapping layer that relates the domain objects
    to the relational tables. Implicitly duplicating that information here could hurt the modifiability and
    maintainability of the Invoice and Customer objects, because any change to their mappings now
    have to be tracked in more than one place. But this example is a simple illustration of how to keep
    the rule in just one place. Some object-relational mapping frameworks provide the means to
    express such a query in terms of the model objects and attributes, generating the actual SQL in
    the infrastructure layer. This would let us have our cake and eat it too."
    («Domain-Driven Design: Tackling Complexity in the Heart of Software» [#fnddd]_)

..

    The greatest value I've seen delivered has been when a narrowly scoped framework automates a
    particularly tedious and error-prone aspect of the design, such as persistence and object-relational
    mapping. The best of these unburden developers of drudge work while leaving them complete
    freedom to design.
    («Domain-Driven Design: Tackling Complexity in the Heart of Software» [#fnddd]_)

Одним из главных принципов объектно ориентированного программирования является инкапсуляция.
Принцип единой обязанности гласит, что каждый объект должен иметь одну обязанность и эта обязанность должна быть полностью инкапсулирована в класс.
Лишая объект поведения, мы возлагаем его поведение на другой объект, который должен обслуживать первый.
Вопрос в том, оправдано ли это?
Если в разделении ActiveRecord на DataMapper и Domain Model это очевидно, и направлено именно на соблюдение принципа единой обязанности, то в данном случае ответ не так очевиден.
Объект поведения начинает "завидовать" объекту данных "G14: Feature Envy" [#fncc]_, ("Feature Envy" [#fnr]_), обретая признаки "F2: Output Arguments" [#fncc]_, "Convert Procedural Design to Objects" [#fnr]_,  "Primitive Obsession" [#fnr]_ и "Data Class" [#fnr]_.
Рассуждения M.Fowler по этому поводу в статье "`Anemic Domain Model`_".

    "High class and method counts are sometimes the result of pointless dogmatism. Consider, for example, a coding standard that insists on creating an interface for each and every class. Or consider developers who insist that fields and behavior must always be separated into data classes and behavior classes. Such dogma should be resisted and a more pragmatic approach adopted."
    («Clean Code: A Handbook of Agile Software Craftsmanship» [#fncc]_)

По поводу второго вопроса.
Из всех ORM, что я встречал в своей практике (не только на Python), поддержка ACID в Storm ORM и SQLAlchemy реализована наилучшим образом.
Надо сказать, в подавляющем большинстве существующих ORM такие попытки даже не предпринимаются.

Martin Fowler reasoning on this point in the article "`Orm Hate`_".

Article "`Dance you Imps! <https://8thlight.com/blog/uncle-bob/2013/10/01/Dance-You-Imps.html>`__" by Robert Martin.

В целом у меня отношение к ORM неоднозначное.
Слишком много существующих ORM создает больше "запахов" в коде, чем устраняет.
Но Storm ORM к ним не относится.


.. rubric:: Footnotes

.. [#fncc] «`Clean Code: A Handbook of Agile Software Craftsmanship`_» `Robert C. Martin`_
.. [#fnr] «`Refactoring: Improving the Design of Existing Code`_» by `Martin Fowler`_, Kent Beck, John Brant, William Opdyke, Don Roberts
.. [#fnpoeaa] «Patterns of Enterprise Application Architecture» by Martin Fowler, David Rice, Matthew Foemmel, Edward Hieatt, Robert Mee, Randy Stafford
.. [#fnddd] «Domain-Driven Design: Tackling Complexity in the Heart of Software» by Eric Evans


.. _Refactoring\: Improving the Design of Existing Code: http://martinfowler.com/books/refactoring.html
.. _Refactoring Ruby Edition: http://martinfowler.com/books/refactoringRubyEd.html
.. _Anemic Domain Model: http://www.martinfowler.com/bliki/AnemicDomainModel.html
.. _Orm Hate: http://martinfowler.com/bliki/OrmHate.html
.. _Martin Fowler: http://martinfowler.com/

.. _ActiveRecord: http://www.martinfowler.com/eaaCatalog/activeRecord.html
.. _Class Table Inheritance: http://martinfowler.com/eaaCatalog/classTableInheritance.html
.. _Concrete Table Inheritance: http://martinfowler.com/eaaCatalog/concreteTableInheritance.html
.. _DataMapper: http://martinfowler.com/eaaCatalog/dataMapper.html
.. _Data Transfer Object: http://martinfowler.com/eaaCatalog/dataTransferObject.html
.. _Domain Model: http://martinfowler.com/eaaCatalog/domainModel.html
.. _Entity Attribute Value: https://en.wikipedia.org/wiki/Entity%E2%80%93attribute%E2%80%93value_model
.. _Gateway: http://martinfowler.com/eaaCatalog/gateway.html
.. _Identity Map: http://martinfowler.com/eaaCatalog/identityMap.html
.. _Query Object: http://martinfowler.com/eaaCatalog/queryObject.html
.. _Repository: http://martinfowler.com/eaaCatalog/repository.html
.. _Service Stub: http://martinfowler.com/eaaCatalog/serviceStub.html
.. _Single Table Inheritance: http://martinfowler.com/eaaCatalog/singleTableInheritance.html
.. _Table Data Gateway: http://martinfowler.com/eaaCatalog/tableDataGateway.html
.. _Transaction Script: http://martinfowler.com/eaaCatalog/transactionScript.html
.. _Unit of Work: http://martinfowler.com/eaaCatalog/unitOfWork.html
.. _Criteria: `Query Object`_
.. _SQLBuilder: `Query Object`_

.. _Introduce Parameter Object: http://www.refactoring.com/catalog/introduceParameterObject
.. _Replace Conditional with Polymorphism: http://www.refactoring.com/catalog/replaceConditionalWithPolymorphism.html

.. _Clean Code\: A Handbook of Agile Software Craftsmanship: http://www.informit.com/store/clean-code-a-handbook-of-agile-software-craftsmanship-9780132350884
.. _Robert C. Martin: http://informit.com/martinseries

.. _SOLID: https://en.wikipedia.org/wiki/SOLID_%28object-oriented_design%29
.. _Open/Closed Principle: https://en.wikipedia.org/wiki/Open/closed_principle
.. _OCP: `Open/Closed Principle`_
.. _Single responsibility principle: https://en.wikipedia.org/wiki/Single_responsibility_principle
.. _SRP: `Single responsibility principle`_

.. _ACID: https://en.wikipedia.org/wiki/ACID
.. _Cohesion: https://en.wikipedia.org/wiki/Cohesion_%28computer_science%29
.. _Composite pattern: https://en.wikipedia.org/wiki/Composite_pattern
.. _DRY: https://en.wikipedia.org/wiki/Don't_repeat_yourself
.. _KISS: https://en.wikipedia.org/wiki/KISS_principle
.. _object: https://docs.python.org/2/library/functions.html#object
.. _Storm ORM: https://storm.canonical.com/
.. _KISS principle: `KISS`_
.. _KISS-style: `KISS`_
.. _postgresql inheritance: http://www.postgresql.org/docs/9.4/static/tutorial-inheritance.html
.. _postgresql inheritance DDL: http://www.postgresql.org/docs/9.4/static/ddl-inherit.html

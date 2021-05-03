
Роль архитектуры в масштабировании команд, DDD и микросервисах
==============================================================

.. post::
   :language: ru
   :tags: DDD, Microservices, Software Architecture, Management, Agile, Scaled Agile
   :category:
   :author: Ivan Zakrevsky

.. May 03, 2021

Данная статья представляет собой компиляцию сообщений с Telegram-channel `@emacsway_log <https://t.me/emacsway_log>`__, и посвящена довольно дискуссионному вопросу о роли архитектуры в масштабируемой Agile-разработке, DDD и Microservices Architecture.


.. contents:: Содержание


Закон Брукса и роль автономности команд
=======================================

Сегодня, наверное, каждый знает Закон Брукса:

    📝 "Если проект не укладывается в сроки, то добавление рабочей силы задержит его ещё больше.

    Adding manpower to a late software project makes it later."

    -- The Brooks's Law

    📝 "Brooks' law is based on the idea that communications overhead is a significant factor on software projects, and that work on a software project is not easily partitioned into isolated, independent tasks. Ten people can pick cotton ten times as fast as one person because the work is almost perfectly partitionable, requiring little communication or coordination. But nine women can't have a baby any faster than one woman can because the work is not partitionable. Brooks argues that work on a software project is more like having a baby than picking cotton. When new staff are brought into a late project, they aren't immediately productive, and they must be trained. The staff who must train them are already productive, but they lose productivity while they're training new staff. Brooks argues that, on balance, more effort is lost to training and additional coordination and communications overhead than is gained when the new staff eventually becomes productive."

    -- Steve McConnell, "`Brooks' Law Repealed? <https://stevemcconnell.com/articles/brooks-law-repealed/>`__"

..

    📝 "Число занятых [специалистов] и число месяцев [в термине человеко-месяц] являются взаимозаменяемыми величинами лишь тогда, когда задачу можно распределить среди ряда работников, которые не имеют между собой взаимосвязи.

    Men and months are interchangeable commodities only when a task can be partitioned among many workers with no communication among them."

    -- "The Mythical Man-Month Essays on Software Engineering Anniversary Edition" by Frederick P. Brooks, Jr.

Сравните это с

    📝 "Microservices' main benefit, in my view, is enabling parallel development by establishing a hard-to-cross boundary between different parts of your system."

    - "`Don't start with a monolith <https://martinfowler.com/articles/dont-start-monolith.html>`__" by Stefan Tilkov, a co-founder and principal consultant at innoQ


Ссылки по теме
==============

1. "`Architecture Ownership Patterns For Team Topologies. Part 1: A Business Architecture Model <https://medium.com/nick-tune-tech-strategy-blog/team-responsibility-ownership-patterns-part-1-a-business-architecture-model-63597c4e60e1>`__" by Nick Tune
#. "`Architecture Ownership Patterns for Team Topologies. Part 2: Single Team Patterns <https://medium.com/nick-tune-tech-strategy-blog/architecture-ownership-patterns-for-team-topologies-part-2-single-team-patterns-943d31854285>`__" by Nick Tune

1. "`Agile Teams <https://www.scaledagileframework.com/agile-teams/>`__"
#. "`Organizing Agile Teams and ARTs: Team Topologies at Scale <https://www.scaledagileframework.com/organizing-agile-teams-and-arts-team-topologies-at-scale/>`__"
#. "`System and Solution Architect/Engineering <https://www.scaledagileframework.com/system-and-solution-architect-engineering/>`__"
#. "`Enterprise Architect <https://www.scaledagileframework.com/enterprise-architect/>`__"
#. "`Architectural Runway <https://www.scaledagileframework.com/architectural-runway/>`__"
#. "`Agile Architecture in SAFe <https://www.scaledagileframework.com/agile-architecture/>`__"

- "`Open Agile Architecture. A Standard of The Open Group <https://pubs.opengroup.org/architecture/o-aa-standard/>`__"

.. .. update:: May 03, 2021

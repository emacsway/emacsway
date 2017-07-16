
Проектирование Сервисных Слоёв
==============================

.. post:: Jul 17, 2017
   :language: ru
   :tags: Design, Architecture
   :category:
   :author: Ivan Zakrevsky

Ошибки проектирования сервисных слоев имеют очень широкое распространение.
Я редко встречал грамотно спроектированные сервисные слои в коммереских проектах.
Эта статья призвана несколько улучшить это положение.


Распространенная проблема Django-приложений
===========================================

Широко распространенная ошибка - использование класса django.db.models.Manager (а то и django.db.models.Model) в качестве сервисного слоя.
Нередко можно встретить, как какой-то метод класса django.db.models.Model принимает в качестве аргумента объект HTTP-запроса django.http.request.HttpRequest, например, для проверки прав.

Объект HTTP-запроса - это логика уровня приложения (application), в то время как класс модели - это логика уровня предметной области (domain), т.е. объекты реального уровня, которые так же называет деловыми регламентами (business rules).

Нижележащий слой не должен ничего знать о вышестоящем слое. Логика уровня домена не должна быть осведомлена о логике уровня приложения.

Классу django.db.models.Manager более всего соответствует класс Finder описанный в «Patterns of Enterprise Application Architecture» [#fnpoeaa]_

    При реализации шлюза записи данных возникает вопрос: куда "пристроить" методы
    поиска, генерирующие экземпляр данного типового решения? Разумеется, можно вос-
    пользоваться статическими методами поиска, однако они исключают возможность по-
    лиморфизма (что могло бы пригодиться, если понадобится определить разные методы
    поиска для различных источников данных). В подобной ситуации часто имеет смысл
    создать отдельные объекты поиска, чтобы у каждой таблицы реляционной базы данных
    был один класс для проведения поиска и один класс шлюза для сохранения результатов
    этого поиска.

    Иногда шлюз записи данных трудно отличить от активной записи (Active Record, 182).
    В этом случае следует обратить внимание на наличие какой-либо логики домена; если
    она есть, значит, это активная запись. Реализация шлюза записи данных должна включать
    в себя только логику доступа к базе данных и никакой логики домена.

    With a Row Data Gateway you're faced with the questions of where to put the find operations that generate this
    pattern. You can use static find methods, but they preclude polymorphism should you want to substitute
    different finder methods for different data sources. In this case it often makes sense to have separate finder
    objects so that each table in a relational database will have one finder class and one gateway class for the results.

    It's often hard to tell the difference between a Row Data Gateway and an Active Record (160). The crux of the
    matter is whether there's any domain logic present; if there is, you have an Active Record (160). A Row Data
    Gateway should contain only database access logic and no domain logic.
    (Chapter 10. "Data Source Architectural Patterns", "Row Data Gateway", «Patterns of Enterprise Application Architecture» [#fnpoeaa]_)

Хотя Django не использует паттерн `Repository`_, она использует абстракцию критериев выборки, своего рода разновидность паттерна `Query Object`_. Подобно паттерну Repository, класс модели (`ActiveRecord`_) ограничивает свой интерфейс посредством интерфейса Query Object. А так как класс  не должен делать предположений о своих клиентах, то накапливать предустановленные запросы в класс модели нельзя, ибо он не может владеть потребностями всех клиентов. Клиенты должны сами заботиться о себе. А сервисный слой как раз и создан для обслуживания клиентов.

Попытки исключить Сервинсый Слой из Django-приложений приводит к появлению менеджеров с огромным количеством методов.

Хорошей практикой было бы сокрытие посредством сервисного слоя способа реализации Django моделей в виде `ActiveRecord`_.
Это позволит безболезненно подменить ORM в случае необходимости.


.. rubric:: Footnotes

.. [#fnpoeaa] «`Patterns of Enterprise Application Architecture`_» by `Martin Fowler`_, David Rice, Matthew Foemmel, Edward Hieatt, Robert Mee, Randy Stafford

.. _ActiveRecord: http://www.martinfowler.com/eaaCatalog/activeRecord.html
.. _Patterns of Enterprise Application Architecture: https://www.martinfowler.com/books/eaa.html
.. _Martin Fowler: https://martinfowler.com/aboutMe.html

.. _Query Object: http://martinfowler.com/eaaCatalog/queryObject.html
.. _Repository: http://martinfowler.com/eaaCatalog/repository.html
.. _Service Layer: https://martinfowler.com/eaaCatalog/serviceLayer.html

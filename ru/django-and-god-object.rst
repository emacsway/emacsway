
Django и Божественный Объект
============================

.. post:: Jan 02, 2018
   :language: ru
   :tags: Django
   :category:
   :author: Ivan Zakrevsky


Божественные Объекты - распространенное явление для Django приложений, поэтому рассмотрим этот вопрос в подробностях.

.. contents:: Содержание

Здесь уместно упомянуть, что эту проблему уже озвучивал небезызвестный Андрей Светлов в статье "`Почему я не люблю конфигурацию в django-style <http://asvetlov.blogspot.com/2015/05/global-config.html>`__". Поэтому, я просто углублюсь в эту тему.

В качестве примера рассмотрим простейшую ситуацию для выдачи файла robots.txt с различным содержимым для staging и production. Будем считать, что ограничить доступ к сайту мы по каким-то причинам не можем, а вариант использования статического сервера не предоставляется облачным сервисом.

Я часто наблюдаю в Django-приложениях нечто подобное:


.. code-block:: python
   :caption: someproject/settings_production.py
   :name: someproject-settings-production-py-v1
   :linenos:

   from .settings import *

   ENVIRONMENT = 'production'


.. code-block:: python
   :caption: robots/urls.py
   :name: robots-urls-py-v1
   :linenos:

   from django.urls import path
   from robots.views import RobotsTxtView


   urlpatterns = [
       path('robots.txt', RobotsTxtView.as_view(
           content_type="text/plain"
       ), name='robots.txt'),
   ]


.. code-block:: python
   :caption: robots/views.py
   :name: robots-views-py-v1
   :linenos:

   from django.conf import settings
   from django.views.generic import TemplateView


   class RobotsTxtView(TemplateView):
       def get_template_names(self):
           if settings.ENVIRONMENT == 'producton':
               return ['robots.production.txt']
           else:
               return ['robots.default.txt']

Знакомая картина, не правда ли?


Волшебные строки (Magic Strings)
================================

Вопрос: а Вы заметили опечатку в строке 7 файла :ref:`robots-views-py-v1`?
Одна такая опечатка чревата выпадением проекта из поискового индекса, что для многих проектов равносильно катастрофе.

Для решения этой проблемы, заменим волшебные строки константами.
Здесь нам пригодится тип данных `Enum <https://docs.python.org/3/library/enum.html>`__.

На первый взгляд, мы могли бы перечислить допустимые значения окружения в файле с настройками проекта.
Но проблема в том, что приложение (application) не может зависеть от конкретного проекта (project).

Зато приложение может зависеть от другого приложения, и объявить зависимости в установочном файле пакета (package).

Итак, создадим дополнительное приложение и назовем его environment.
Создадим в нем файл constants.py.

Здесь возникает вопрос по поводу соглашения именования.
Когда переменная является одновременно и именем класса, и константой, то какое именование предпочесть?
Мое мнение склоняется ко второму варианту.


.. code-block:: python
   :caption: someproject/settings_production.py
   :name: someproject-settings-production-py-v2
   :linenos:

   from .settings import *
   from environment.constants import AVAILABLE_ENVIRONMENT

   ENVIRONMENT = AVAILABLE_ENVIRONMENT.PRODUCTION


.. code-block:: python
   :caption: environment/constants.py
   :name: environment-constants-py-v2
   :linenos:

   from enum import IntEnum, unique


   @unique
   class AVAILABLE_ENVIRONMENT(IntEnum):
       LOCAL = 1
       DEVELOPMENT = 2
       STAGING = 3
       PRODUCTION = 4

   AVAILABLE_ENVIRONMENT.do_not_call_in_templates = True


.. code-block:: python
   :caption: robots/views.py
   :name: robots-views-py-v2
   :linenos:

   from django.conf import settings
   from django.views.generic import TemplateView
   from environment.constants import AVAILABLE_ENVIRONMENT


   class RobotsTxtView(TemplateView):
       def get_template_names(self):
           if settings.ENVIRONMENT == AVAILABLE_ENVIRONMENT.PRODUCTION:
               return ['robots.production.txt']
           else:
               return ['robots.default.txt']


Божественный Объект (God Object)
================================

Ок, мы застраховались от случайной опечатки.
Следующая проблема имеет название "Божественный Объект" ("`God Object <http://wiki.c2.com/?GodObject>`__").


Проблема с тестированием
------------------------

Как нам убедиться что этот класс будет работать во всех окружениях?
Что если мы забыли загрузить какой-то templatetag в шаблоне ``robots.production.txt``?
Итак, мы должны протестировать класс RobotsTxtView для всех окружений, в том числе и для PRODUCTION-окружения, при этом реально находясь в LOCAL-окружении.

Но как нам протестировать этот класс для всех окружений, не изменяя самих окружений?
Если я переопределю значение settings.ENVIRONMENT согласно документации, используя `@override_settings(ENVIRONMENT=AVAILABLE_ENVIRONMENT.PRODUCTION) <https://docs.djangoproject.com/en/2.0/topics/testing/tools/#django.test.override_settings>`__, то где гарантия, что я не изменю поведения какой-нибудь Middleware, использующей этот же параметр конфига?

Да, в Django есть небольшие трудности с изолированными юнит-тестами, которые решаются принципами "Чистой Архитектуры", к этому вопросу мы еще вернемся чуть позже.
А пока нам нужно подменить значение окружения для класса, и при этом не затронуть его для всех остальных компонентов сайта.


Брешь в инкапсуляции
--------------------

Проблема обращения метода к глобальной переменной заключается в том, что она образует брешь в инкапсуляции.
А инкапсуляция создана для защиты абстракции, которая, в свою очередь, создана укрощения сложности.

Нарушив инкапсуляцию всего одной глобальной переменной, мы уже больше не можем рассматривать отдельно взятый метод.
Мы должны так же осознать все обращения к этой глобальной переменной по всей программе.
Декомпозиция сложности нарушена. Ее последствия я уже рассматривал в статье ":doc:`../en/how-to-quickly-develop-high-quality-code`".
А пока просто напомню, что рост сложности программы снижает темпы ее разработки, и делает разработку дорогой.


"Завистливые функции" (Code Smell "Feature Envy")
-------------------------------------------------

Вы заметили, что наш класс RobotsTxtView интересуется данным другого класса (django.conf.Settings)?

    Завистливые функции

    Весь смысл объектов в том, что они позволяют хранить данные вместе
    с процедурами их обработки. Классический пример дурного запаха -
    метод, который больше интересуется не тем классом, в котором он на
    ходится, а каким-то другим. Чаще всего предметом зависти являются
    данные.

    Feature Envy

    The whole point of objects is that they are a technique to package data with the processes used
    on that data. A classic smell is a method that seems more interested in a class other than the one
    it actually is in. The most common focus of the envy is the data.

    ("Refactoring: Improving the Design of Existing Code" [#fnrefactoring]_ by Martin Fowler, Kent Beck, John Brant, William Opdyke, Don Roberts)


Повышенное сопряжение (High Coupling)
-------------------------------------

Вы заметили, что класс RobotsTxtView должен быть осведемленным об интерфейсе/структуре объекта settings?

Хорошая программа сопровождается "Низким Сопряжением (Зацеплением) и Высокой Связанностью" ("`Low coupling & High cohesion <http://wiki.c2.com/?CouplingAndCohesion>`__").

Существуют Push и Pull модели данных.
В первом случае приложение должно установить зависимости в объект.
Во втором случае, объект должен запросить зависимости у приложения.

Проблема в том, что для того, чтобы запросить, объект должен быть осведомлен об интерфейсе, по которому он может это сделать.
А это - лишнее Сопряжение (Coupling), которое снижает повторную используемость класса.
Что если Вы захотите использовать класс в другом приложении, которое имеет другой интерфейс для запросов?

В этом и заключается превосходство "Пассивного Внедрения Зависимостей" ("Passive Dependency Injection") [#fnccode]_ над "Локатором Служб" ("Service locator"), смотрите более подробно в статье "`Inversion of Control Containers and the Dependency Injection pattern <https://martinfowler.com/articles/injection.html>`__" by Martin Fowler.


Решение
-------

Самый простой способ локазизовать эту настройку - это параметризация объекта при помощи конструктора.


.. code-block:: python
   :caption: robots/urls.py
   :name: robots-urls-py-v3
   :linenos:

   from django.conf import settings
   from django.urls import path
   from robots.views import RobotsTxtView


   urlpatterns = [
       path('robots.txt', RobotsTxtView.as_view(
           content_type="text/plain",
           environment=settings.ENVIRONMENT
       ), name='robots.txt'),
   ]


.. code-block:: python
   :caption: robots/views.py
   :name: robots-views-py-v3
   :linenos:

   from django.views.generic import TemplateView
   from environment.constants import AVAILABLE_ENVIRONMENT


   class RobotsTxtView(TemplateView):
       AVAILABLE_ENVIRONMENT = AVAILABLE_ENVIRONMENT
       environment = None

       def __init__(self, *args, **kwargs):
           super().__init__(*args, **kwargs)
           self.environment = kwargs['environment']

       def get_template_names(self):
           if settings.ENVIRONMENT == self.AVAILABLE_ENVIRONMENT.PRODUCTION:
               return ['robots.production.txt']
           else:
               return ['robots.default.txt']

Я так же разместил константу AVAILABLE_ENVIRONMENT в пространстве имен класса, чтобы на нее распространялась концепция наследования.


Code Smell "Switch Statements"
==============================

Как уже отмечалось ранее, "Весь смысл объектов в том, что они позволяют хранить данные вместе с процедурами их обработки." ("Refactoring: Improving the Design of Existing Code" [#fnrefactoring]_).
Объект должен обладать свойственным ему поведением, иначе весь смысл существования объектов теряется, а парадигма программирования превращается из объекто-ориентированной в процедурную.

Чтобы сохранить смысл объектов, условные операторы должны не управлять поведением объекта, а создавать объект с нужным поведением.
Т.е. они должны использоваться в Абстрактной Фабрике, Фабричном Методе, или просто в конструкторе объекта.

    Операторы типа switch

    Одним из очевидных признаков объектно-ориентированного кода служит сравнительная
    немногочисленность операторов типа switch (или case). Проблема, обусловленная применением switch, по
    существу, связана с дублированием. Часто один и тот же блок switch оказывается разбросанным по разным
    местам программы. При добавлении в переключатель нового варианта приходится искать все эти блоки switch
    и модифицировать их. Понятие полиморфизма в ООП предоставляет элегантный способ справиться с этой
    проблемой.

    Как правило, заметив блок switch, следует подумать о полиморфизме. Задача состоит в том, чтобы
    определить, где должен происходить полиморфизм. Часто переключатель работает в зависимости от кода типа.
    Необходим метод или класс, хранящий значение кода типа. Поэтому воспользуйтесь «Выделением
    метода» (Extract Method ) для выделения переключателя, а затем «Перемещением метода» (Move Method ) для
    вставки его в тот класс, где требуется полиморфизм. В этот момент следует решить, чем воспользоваться-
    «Заменой кода типа подклассами» (Replace Type Code with Subclasses ) или «Заменой кода типа
    состоянием/стратегией» (Replace Type Code with State / Strategy ). Определив структуру наследования, можно
    применить «Замену условного оператора полиморфизмом» (Replace Conditional with Polymorphism ).

    Если есть лишь несколько вариантов переключателя, управляющих одним методом, и не предполагается
    их изменение, то применение полиморфизма оказывается чрезмерным. В данном случае хорошим выбором
    будет «Замена параметра явными методами» (Replace Parameter with Explicit Method ). Если одним из вариантов
    является null, попробуйте прибегнуть к «Введению объекта Null» (Introduce Null Object ).

    Switch Statements

    One of the most obvious symptoms of object-oriented code is its comparative lack of switch (or
    case) statements. The problem with switch statements is essentially that of duplication. Often you
    find the same switch statement scattered about a program in different places. If you add a new
    clause to the switch, you have to find all these switch, statements and change them. The
    object-oriented notion of polymorphism gives you an elegant way to deal with this problem.

    Most times you see a switch statement you should consider polymorphism. The issue is where
    the polymorphism should occur. Often the switch statement switches on a type code. You want
    the method or class that hosts the type code value. So use Extract Method to extract the switch
    statement and then Move Method to get it onto the class where the polymorphism is needed. At
    that point you have to decide whether to Replace Type Code with Subclasses or Replace
    Type Code with State/Strategy. When you have set up the inheritance structure, you can use
    Replace Conditional with Polymorphism.

    If you only have a few cases that affect a single method, and you don't expect them to change,
    then polymorphism is overkill. In this case Replace Parameter with Explicit Methods is a
    good option. If one of your conditional cases is a null, try Introduce Null Object.

    ("Refactoring: Improving the Design of Existing Code" [#fnrefactoring]_ by Martin Fowler, Kent Beck, John Brant, William Opdyke, Don Roberts)

..

    G23: Используйте полиморфизм

    Вместо if/Else или switch/Case
    Я использую правило «ОДНОЙ КОМАНДЫ SWITCH»: для каждого типа
    выбора программа не должна содержать более одной команды switch. Множественные
    конструкции switch следует заменять полиморфными объектами.

    G23: Prefer Polymorphism to If/Else or Switch/Case

    I use the following “ONE SWITCH” rule: There may be no more than one switch
    statement for a given type of selection. The cases in that switch statement must create
    polymorphic objects that take the place of other such switch statements in the rest of the system.

    ("Clean Code: A Handbook of Agile Software Craftsmanship" [#fnccode]_ by Robert C. Martin)

Вообще-то проблема не так и страшна, и с ней можно было бы и смириться по совету Мартина Фаулера.
Но мы пойдем дальше.

Есть два способа решить эту проблему, простой ("Replace Subclass with Fields") [#fnrefactoring]_ и чистый ("Replace Type Code with State/Strategy") [#fnrefactoring]_.


Простое решение
---------------

Если внимательно изучить класс ``django.views.generic.base.TemplateView``, то можно заметить, что он реализует метод "`Replace Subclass with Fields <https://www.refactoring.com/catalog/replaceSubclassWithFields.html>`__" [#fnrefactoring]_.
А потому, нет причин этим не воспользоваться.
Все что от нас требуется - это переместить условные операторы из метода объекта (т.е. его поведения) в его конструктор.


.. code-block:: python
   :caption: robots/views.py
   :name: robots-views-py-v4
   :linenos:

   from django.views.generic import TemplateView
   from environment.constants import AVAILABLE_ENVIRONMENT


   class RobotsTxtView(TemplateView):
       AVAILABLE_ENVIRONMENT = AVAILABLE_ENVIRONMENT
       template_name = 'robots.default.txt'

       def __init__(self, *args, **kwargs):
           super().__init__(*args, **kwargs)
           assert 'environment' in kwargs
           assert kwargs['environment'] in self.AVAILABLE_ENVIRONMENT
           if kwargs['environment'] == self.AVAILABLE_ENVIRONMENT.PRODUCTION:
               self.template_name = 'robots.production.txt'


Чистое решение
--------------

Чистое решение заключается в реализации метода "`Replace Type Code with State/Strategy <https://www.refactoring.com/catalog/replaceTypeCodeWithStateStrategy.html>`__" [#fnrefactoring]_.


.. code-block:: python
   :caption: robots/views.py
   :name: robots-views-py-v5
   :linenos:

   import collections.abc
   from django.views.generic import TemplateView


   class DefaultTemplateNamesAccessor(collections.abc.Callable):
       def __call__(self):
           return ['robots.default.txt']


   class ProductionTemplateNamesAccessor(collections.abc.Callable):
       def __call__(self):
           return ['robots.production.txt']


   class RobotsTxtView(TemplateView):
       def __init__(self, *args, **kwargs):
           super().__init__(*args, **kwargs)
           assert 'template_names_accessor' in kwargs
           self.get_template_names = template_names_accessor


.. code-block:: python
   :caption: robots/factory.py
   :name: robots-factory-py-v5
   :linenos:

   from environment.constants import AVAILABLE_ENVIRONMENT
   from robots import views

   class RobotsFactory:
       AVAILABLE_ENVIRONMENT = AVAILABLE_ENVIRONMENT

       @classmethod
       def make_robots_txt_view(cls, environment):
           return views.RobotsTxtView.as_view(
               content_type="text/plain",
               template_names_accessor=cls._make_template_names_accessor(environment)
           )

       @classmethod
       def _make_template_names_accessor(cls, environment):
           assert environment in AVAILABLE_ENVIRONMENT
           if environment == AVAILABLE_ENVIRONMENT.PRODUCTION:
               return cls._make_production_template_names_accessor()
           return cls._make_default_template_names_accessor()
       
       @staticmethod
       def _make_default_template_names_accessor():
           return views.DefaultTemplateNamesAccessor()

       @staticmethod
       def _make_production_template_names_accessor():
           return views.ProductionTemplateNamesAccessor()


.. code-block:: python
   :caption: robots/urls.py
   :name: robots-urls-py-v5
   :linenos:

   from django.urls import path
   from robots.factory import RobotsFactory


   urlpatterns = [
       path('robots.txt', RobotsFactory.make_robots_txt_view(), name='robots.txt'),
   ]


Как видите, чистое решение оказалось намного более многословным. Какое же решение предпочесть?

Лично я всегда следую принципу "Designing Through Refactoring" [#fnxp]_, и, в соответствии с принципом Экстремального Программирования "The simplest thing that could possibly work", - всегда достигаю мнинимально-необходимого уровня косвенности (inderection).

Если решение простое, и оно работает (т.е. проходит тесты), и оно не содержит дубликатов, - то работа завершена.
Не должно быть принципов ради принципов.
Каждый принцип должен решать какую-то конкретную задачу. Если он ничего не решает, то он - лишний.

Не существует хороших или плохих решений.
Все дело - в достигаемом результате.
Задача Agile-методологии - поддерживать стоимость изменения программы низкой.
Если эта цель соблюдена - нет смысла усложнять дальше. Любое усложнение - это удорожание стоимости изменения программы.


.. rubric:: Footnotes

.. [#fnccode] "`Clean Code: A Handbook of Agile Software Craftsmanship`_" by `Robert C. Martin`_
.. [#fnrefactoring] "`Refactoring: Improving the Design of Existing Code`_" by `Martin Fowler`_, Kent Beck, John Brant, William Opdyke, Don Roberts
.. [#fnxp] "`Extreme Programming Explained`_" by Kent Beck


.. update:: Jan 02, 2018


.. _Clean Code\: A Handbook of Agile Software Craftsmanship: http://www.informit.com/store/clean-code-a-handbook-of-agile-software-craftsmanship-9780132350884
.. _Robert C. Martin: http://informit.com/martinseries
.. _Refactoring\: Improving the Design of Existing Code: https://martinfowler.com/books/refactoring.html
.. _Martin Fowler: https://martinfowler.com/aboutMe.html
.. _Extreme Programming Explained: http://www.informit.com/store/extreme-programming-explained-embrace-change-9780321278654

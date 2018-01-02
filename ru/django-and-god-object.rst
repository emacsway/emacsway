
Django и Божественный Объект
============================

.. post:: Jan 02, 2018
   :language: ru
   :tags: Django
   :category:
   :author: Ivan Zakrevsky


Божественные Объекты - распространенное явление для Django приложений, поэтому рассмотрим этот вопрос в подробностях.

Здесь уместно упомянуть, что эту проблему уже озвучивал небезызвестный Андрей Светлов в статье "`Почему я не люблю конфигурацию в django-style <http://asvetlov.blogspot.com/2015/05/global-config.html>`__". Поэтому, я просто углублюсь в эту тему.

В качестве примера рассмотрим простейшую ситуацию для выдачи файла robots.txt с различным содержимым для staging и production. Будем считать, что ограничить доступ к сайту мы по каким-то причинам не можем, а вариант использования статического сервера не предоставляется облачным сервисом.

Я часто наблюдаю в Django-приложениях нечто подобное:


.. code-block:: python
   :caption: someproject/settings_production.py
   :name: someproject-settings-production-py-v1
   :linenos:

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


Волшебные строки (Magic Strings)
================================

Вопрос - Вы заметили опечатку в строке 7 файла :ref:`robots-views-py-v1`?
Одна такая опечатка чревата выпадением проекта из поискового индекса, что для многих проектов равносильно катастрофе.

Для решения этой проблемы, заменим волшебные строки константами.
Здесь нам пригодится тип данных `Enum <https://docs.python.org/3/library/enum.html>`__.

На первый взгляд, мы могли бы перечислить допустимые значения окружения в файле с настройками проекта.
Но проблема в том, что приложение (application) не может зависеть от конкретного проекта (project).

Зато приложение может зависеть от другого приложения, и иметь объявленные зависимости в установочном файле пакета (package).

Итак, создадим дополнительное приложение и назовем его environment.
Создадим в нем файл constants.py.

Здесь возникает вопрос по поводу соглашения именования.
Когда переменная является одновременно и именем класса, и константой, то какое именование предпочесть?
Мое мнение склоняется ко второму варианту.


.. code-block:: python
   :caption: someproject/settings_production.py
   :name: someproject-settings-production-py-v2
   :linenos:

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

Как нам убедиться что этот класс будет работать во всех окружениях?
Что если мы забыли загрузить какой-то templatetag в шаблоне ``robots.production.txt``?
Итак, мы должны протестировать класс RobotsTxtView для всех окружений, в том числе и для PRODUCTION-окружения, при этом реально находясь в LOCAL-окружении.

Но как нам протестировать этот класс для всех окружений, не изменяя самих окружений?
Если я переопределю значение settings.ENVIRONMENT согласно документации, используя `@override_settings(ENVIRONMENT=AVAILABLE_ENVIRONMENT.PRODUCTION) <https://docs.djangoproject.com/en/2.0/topics/testing/tools/#django.test.override_settings>`__, то где гарантия, что я не изменю поведения какой-нибудь Middleware, использующей этот же параметр конфига?

Да, в Django есть небольшие трудности с изолированными юнит-тестами, которые решаются принципами "Чистой Архитектуры", к этому вопросу мы еще вернемся чуть позже.
А пока нам нужно подменить значение окружения для класса, и при этом не затронуть его для всех остальных компонентов сайта.

Самый простой способ локазизовать эту настройку - это параметризация конструктора.


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
       environment = None

       def __init__(self, *args, **kwargs):
           super().__init__(*args, **kwargs)
           self.environment = kwargs['environment']

       def get_template_names(self):
           if settings.ENVIRONMENT == AVAILABLE_ENVIRONMENT.PRODUCTION:
               return ['robots.production.txt']
           else:
               return ['robots.default.txt']


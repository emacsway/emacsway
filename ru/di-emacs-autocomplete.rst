
.. emacsway post example, created by `ablog start` on Oct 09, 2015.

.. post:: Oct 09, 2015
   :language: ru
   :tags: Emacs, Dependency Injection, autocomplete, Python
   :author: Ivan Zakrevsky

Emacs autocomplete and Dependency injection (DI)
================================================

В пассивных классах, которым `зависимости внедряет <http://www.martinfowler.com/articles/injection.html>`__ программа, возникают трудности с автокомплитом в `emacs <https://www.gnu.org/software/emacs/>`__ с `elpy-mode <https://github.com/jorgenschaefer/elpy>`__.

Вариантов решения здесь несколько.

#. Устанавливать зависимости через конструктор класса, учитывая, что бэкенд `jedi <https://github.com/davidhalter/jedi>`__ `учитывает типы аргументов функций и возвращаемых значений, указанных в докстрингах <http://jedi.jedidjah.ch/en/latest/docs/features.html#type-hinting>`__.
#. Устанавливать и получать зависимость через геттер и сеттер. В отличии от первого варианта, работать будет декларация типов возвращаемых значений, а не аргументов.
#. Использовать `Service Locator <http://www.martinfowler.com/articles/injection.html>`__ или паттерн `Plugin <http://martinfowler.com/eaaCatalog/plugin.html>`__, которые инициируют запрос и делегируют его исполнение резольверу зависимостей.

Но мы пойдем самым сложным путем, и заставим emacs решать эту проблему, параллельно `попросив разработчиков <https://github.com/davidhalter/jedi/issues/631>`__ jedi обеспечить автокомплит на основании типов атрибутов класса, указанных в докстрингах класса.

Итак.

\1. Стартуем интерпретатор ``M-x run-python`` (предварительно настраиваем elpy на использование ipython чтобы автокомплит работал и в шеле тоже)::

    (when (executable-find "ipython") (elpy-use-ipython))

\2. посылаем в интерпретатор файл с которым работаем: ``M-x python-shell-send-file``.

\3. определяем в интерпретаторе переменную, которая нужна. В моем случае нужна ``self.dao.engine``. Делаем в шелле что-то типа
``self = StatsFactory().make_api()``
у которого по счастливому стечению обстоятельств есть атрибут .dao.engine, который мне и нужен.

В итоге в интерпретаторе будет объявлена переменная ``self.dao.engine``.

\4. Поскольку `elpy заглушает вызов completion-at-point <https://github.com/jorgenschaefer/elpy/blob/3e7e08d14998063ce254cd1934786e7e212b99e3/elpy.el#L3101>`__ в дропдауне company-mode, вызываем вручную ``M-x completion-at-point`` или ``M-x python-shell-completion-complete-or-indent``.

Чтобы не вызывать вручную, биндим их на любую удобную комбинацию клавиш, например "``C-c TAB``".

\5. Таким образом можно автокомплитить любые недостающие переменные, - просто объявляем их в интерпретаторе, и они будут подсвечиваться в буфере редактирования файла.

Профит.

P.S.: это старейшая возможность питон-мода, которую уже многие отвыкли использовать, разбаловавшись разного рода джедаями и ропами)) `IDLE <https://docs.python.org/3/library/idle.html>`__ работает по аналогичному принципу.

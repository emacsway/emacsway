
О книге "Refactoring" by M.Fowler
=================================

.. post:: Nov 01, 2015
   :language: ru
   :tags: Python, refactoring, Fowler
   :category:
   :author: Ivan Zakrevsky

Хочу ответить на уже ставший популярным вопрос, нужно ли читать 
«`Refactoring: Improving the Design of Existing Code <http://martinfowler.com/books/refactoring.html>`__» by Martin Fowler, Kent Beck, John Brant, William Opdyke, Don Roberts
если уже прочитал
«`Clean Code. A Handbook of Agile Software Craftsmanship. <http://www.informit.com/store/clean-code-a-handbook-of-agile-software-craftsmanship-9780132350884>`__» by Robert C. Martin?

Ответ, да, нужно. И не потому, что она будет полнее второй книги, поскольку вторая писалась с оглядкой на первую.

Там есть ответ на главный вопрос: *Нужно ли выделять время на рефакторинг и как убедить в этом руководство?*

Правильный ответ, - время выделять не нужно, а шансов убедить руководство не так и много (главы "What Do I Tell My Manager?" и "When Should You Refactor?").

    "Конечно, многие говорят, что главное для них качество, а на самом деле главное для них – выполнение графика работ.
    В таких случаях я даю несколько спорный совет: не говорите им ничего!

    Подрывная деятельность? Не думаю. Разработчики программного обеспечения – это профессионалы.
    Наша работа состоит в том, чтобы создавать эффективные программы как можно быстрее.
    По моему опыту, рефакторинг значительно способствует быстрому созданию приложений.
    Если мне надо добавить новую функцию, а проект плохо согласуется с модификацией,
    то быстрее сначала изменить его структуру,
    а потом добавлять новую функцию.
    Если требуется исправить ошибку, то необходимо сначала понять, как работает программа,
    и я считаю, что быстрее всего можно сделать это с помощью рефакторинга.
    Руководитель, подгоняемый графиком работ, хочет, чтобы я сделал
    свою работу как можно быстрее; как мне это удастся – мое дело.
    Самый быстрый путь – рефакторинг, поэтому я и буду им заниматься."

    "Of course, many people say they are driven by quality but are more driven by schedule. In these
    cases I give my more controversial advice: Don't tell!

    Subversive? I don't think so. Software developers are professionals. Our job is to build effective
    software as rapidly as we can. My experience is that refactoring is a big aid to building software
    quickly. If I need to add a new function and the design does not suit the change, I find it's quicker
    to refactor first and then add the function. If I need to fix a bug, I need to understand how the
    software works—and I find refactoring is the fastest way to do this. A schedule-driven manager
    wants me to do things the fastest way I can; how I do it is my business. The fastest way is to
    refactor; therefore I refactor."
    ("Refactoring: Improving the Design of Existing Code", Martin Fowler)

Все дело в правильных привычках, благодаря которым код маленькими шажками преобразуется во время выполнения обычных тасков. Главное, - там рассказывается, как сделать эти шаги минимальными, и парировать главный контраргумент: "если я это изменю, то полсайта сломается". Не сломается. Там рассказано как изолировать изменения (глава "Problems with Refactoring").

    "Я не считаю себя замечательным программистом. Я просто хороший программист с замечательными привычками."

    "I'm not a great programmer; I'm just a good programmer with great habits." (Kent Beck)

Если кто-то считает что книга уже стара, то в 2009 году в книге «`Refactoring Ruby Edition <http://martinfowler.com/books/refactoringRubyEd.html>`__» M.Fowler подтвердил актуальность первой книги:

    I Have the Original Book—Should I Get This?
    Probably not. If you’re familiar with the original book you won’t find a lot
    of new material here. You’ll need to adjust the original refactorings to the Ruby
    language, but if you’re like us you shouldn’t find that an inordinate challenge.
    There are a couple of reasons where we think an owner of the original book
    might consider getting a copy of the Ruby edition. The first reason is if you’re
    not too familiar with Java and found the original book hard to follow because
    of that unfamiliarity. If so we hope you find a Ruby-focused book easier to
    work with. The second reason is if you’re leading a Ruby team that has people
    who would struggle with the original book’s Java focus. In that case a Ruby
    book would be a better tool to help pass on your understanding of refactoring.

Есть один момент, - чтобы ее читать, нужно знать «Design Patterns: Elements of Reusable Object-Oriented Software» by Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides и «Patterns of Enterprise Application Architecture» by Martin Fowler, David Rice, Matthew Foemmel, Edward Hieatt, Robert Mee, Randy Stafford, иначе будет сложно понимать.

Да и вообще, единственная проблема, из-за которой рефакторинг часто не практикуется - это отсутствие единого мнения в команде на расслоение архитектуры и распределение обязанностей классов. Из-за чего сложно проводить маленькие шажки, так как другой разработчик на полдороге может совершить маленькие шажки в другую сторону. Эти вопросы M.Fowler тоже рассматривает, как согласовать мнение всех разработчиков (главы "Refactor As You Do a Code Review" и "Refactoring Safely").


Систематизированные каталоги
----------------------------

Каталог рефакторингов "`Catalog of Refactorings <http://www.refactoring.com/catalog/>`__" на http://www.refactoring.com/ и каталог "запахов" кода и эвристических правил "Smells and Heuristics" из книги «Clean Code. A Handbook of Agile Software Craftsmanship.» можно применять при Code Review, освобождая время от необходимости объяснять почему и как нужно исправить код (достаточно просто сослаться на конкретное правило).

Систематизированная форма этих знаний легко входит в привычку, а значит, может сделать работу всей команды согласованной при наименьших затратах времени.


Философия рефакторинга
----------------------

Одно правило мне показалось особенно важным для наших, славянских ребят (и меня в том числе), которые нередко увлекаются поиском совершенства в коде. Поэтому я решил его процитировать:

    "До введения рефакторинга в свою работу я всегда искал гибкие решения.
    Для каждого технического требования я рассматривал возможности его изменения в течение срока жизни системы.
    Поскольку изменения в проекте были дорогостоящими, я старался создать проект, способный выдержать изменения, которые я мог предвидеть.
    Недостаток гибких решений в том, что за гибкость приходится платить.
    Гибкие решения сложнее обычных.
    Создаваемые по ним программы в целом труднее сопровождать, хотя и легче перенацеливать в том направлении, которое предполагалось изначально.
    И даже такие решения не избавляют от необходимости разбираться, как модифицировать проект.
    Для одной двух функций это сделать не очень трудно, но изменения происходят по всей системе.
    Если предусматривать гибкость во всех этих местах, то вся система становится значительно сложнее и дороже в сопровождении.
    Весьма разочаровывает, конечно, то, что вся эта гибкость и не нужна.
    Потребуется лишь какая то часть ее, но невозможно заранее сказать какая.

    Чтобы достичь гибкости, приходится вводить ее гораздо больше, чем требуется в действительности.
    Рефакторинг предоставляет другой подход к рискам модификации.
    Возможные изменения все равно надо пытаться предвидеть, как и рассматривать гибкие решения.
    Но вместо реализации этих гибких решений следует задаться вопросом:
    «Насколько сложно будет с помощью рефакторинга преобразовать обычное решение в гибкое?»
    Если, как чаще всего случается, ответ будет «весьма несложно», то надо просто реализовать обычное решение.

    Рефакторинг позволяет создавать более простые проекты, не жертвуя гибкостью,
    благодаря чему процесс проектирования становится более легким и менее напряженным.
    Научившись в целом распознавать то, что легко поддается рефакторингу, о гибкости решений даже перестаешь задумываться.
    Появляется уверенность в возможности применения рефакторинга, когда это понадобится.
    Создаются самые простые решения, которые могут работать, а гибкие и сложные решения по большей части не потребуются."

    "Before I used refactoring, I always looked for flexible solutions. With any requirement I would
    wonder how that requirement would change during the life of the system. Because design
    changes were expensive, I would look to build a design that would stand up to the changes I
    could foresee. The problem with building a flexible solution is that flexibility costs. Flexible
    solutions are more complex than simple ones. The resulting software is more difficult to maintain
    in general, although it is easier to flex in the direction I had in mind. Even there, however, you
    have to understand how to flex the design. For one or two aspects this is no big deal, but
    changes occur throughout the system. Building flexibility in all these places makes the overall
    system a lot more complex and expensive to maintain. The big frustration, of course, is that all
    this flexibility is not needed. Some of it is, but it's impossible to predict which pieces those are. To
    gain flexibility, you are forced to put in a lot more flexibility than you actually need.

    With refactoring you approach the risks of change differently. You still think about potential
    changes, you still consider flexible solutions. But instead of implementing these flexible solutions,
    you ask yourself, "How difficult is it going to be to refactor a simple solution into the flexible
    solution?" If, as happens most of the time, the answer is "pretty easy," then you just implement
    the simple solution.

    Refactoring can lead to simpler designs without sacrificing flexibility. This makes the design
    process easier and less stressful. Once you have a broad sense of things that refactor easily, you
    57don't even think of the flexible solutions. You have the confidence to refactor if the time comes.
    You build the simplest thing that can possibly work. As for the flexible, complex design, most of
    the time you aren't going to need it."
    ("Refactoring: Improving the Design of Existing Code", Martin Fowler)


Чистота кода кроется в его честности
------------------------------------

Эта фраза заставила меня по новому взглянуть на определение "чистого кода".

    "Потратив немного времени на рефакторинг, можно добиться того, что код станет лучше информировать о своей цели. В таком режиме суть программирования состоит в том, чтобы точно сказать, что вы имеете в виду."

    "A little time spent refactoring can make the code better communicate its purpose. Programming in this mode is all about saying exactly what you mean."
    ("Refactoring: Improving the Design of Existing Code", Martin Fowler)

Я пришел к умозаключению, что стремление к чистому коду - это стремление к истине, и устранение лжи. Основная проблема запутанного кода - введение в заблуждение. Ложь - его единственная проблема. Чистый код выражает о себе точную и правдивую информацию. Чистый код - это способ достижения истины.

**Чистота кода - это способность кода выражать о себе правду, а не вводить в заблуждение.**

Задача рефакторинга - обеспечить возможность легко понимать и изменять код.

Я так же по новому взглянул на определение красоты. Красота - это, на самом деле, простота, когда нет ничего лишнего. Вообразите легковый автомобиль с колесамим от трактора МТЗ, которые, мягко говоря, излишни и по габаритам, и по назначению. Красиво? Кто-то красиво сказал, что идеал - это когда нечего добавить, и нечего отнять.

Удивительно, но суть честности тоже заключается в простоте, - чтобы освободиться от всего лишнего, ненужного, и оставить только то, что действительно имеет значение. Эти слова и отличаются-то всего двумя буквами, "чистый" и "чЕстНый". Ненужность лжи кроется в ее бесполезности, и даже вредности, - она отнимает ресурсы. Она не нужна. Поэтому она портит красоту кода. Robert C. Martin в книге «Clean Code. A Handbook of Agile Software Craftsmanship.» много говорит о лжи в коде, и как от нее освободиться.

Принцип простоты вылился в целое философское направление `KISS principle <https://en.wikipedia.org/wiki/KISS_principle>`__.

Деятельность программиста во многом напоминает мне работу скульптора. Нужно увидеть образ, и отсечь от него все лишнее. Освободить образ, проявить его, т.е. явить его в явь.

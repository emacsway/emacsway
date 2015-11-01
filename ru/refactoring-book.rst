
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

Ответ, да, нужно. И не потому, что она будет полнее второй книги, так как вторая писалась с учетом первой.

Там есть ответ на главный вопрос: *Нужно ли выделять время на рефакторинг и как убедить в этом руководство?*

Правильный ответ, - время выделять не нужно, и руководство вы не убедите (глава "What Do I Tell My Manager?" и "When Should You Refactor?").

    Of course, many people say they are driven by quality but are more driven by schedule. In these
    cases I give my more controversial advice: Don't tell!

    Subversive? I don't think so. Software developers are professionals. Our job is to build effective
    software as rapidly as we can. My experience is that refactoring is a big aid to building software
    quickly. If I need to add a new function and the design does not suit the change, I find it's quicker
    to refactor first and then add the function. If I need to fix a bug, I need to understand how the
    software works—and I find refactoring is the fastest way to do this. A schedule-driven manager
    wants me to do things the fastest way I can; how I do it is my business. The fastest way is to
    refactor; therefore I refactor.

Все дело в правильных привычках, благодаря которым код маленькими шажками преобразуется во время выполнения обычных тасков. Главное, - там рассказывается, как сделать эти шаги минимальными, и парировать главный контраргумент: "если я это изменю, то полсайта сломается". Не сломается. Там рассказано как изолировать изменения (глава "Problems with Refactoring").

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

Единственная загвоздка, - чтобы ее читать, нужно сперва прочитать «Design Patterns: Elements of Reusable Object-Oriented Software» by Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides и «Patterns of Enterprise Application Architecture» by Martin Fowler, David Rice, Matthew Foemmel, Edward Hieatt, Robert Mee, Randy Stafford, иначе будет сложно понимать.

Да и вообще, единственная проблема, из-за которой рефакторинг часто не практикуется - это отсутствие единого мнения в команде на расслоение архитектуры и распределение обязанностей классов. Из-за чего сложно проводить маленькие шажки, так как другой разработчик совершит маленькие шажки в другую сторону. Эти вопросы M.Fowler тоже рассматривает, как согласовать мнение всех разработчиков (глава "Refactor As You Do a Code Review").


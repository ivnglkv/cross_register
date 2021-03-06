# Работа с репозиторием

Последующий текст (и ссылки в нём) предполагает, что вы работаете от
пользователя `kris97` над задачей #15.

**Не копируйте команды на выполнение бездумно!**

## Начало работы

Для начала нужно создать собственную копию репозитория. Для этого нажмите
кнопку "Форк" в боковом меню. На отобразившейся странице можно оставить все
настройки по умолчанию и нажать кнопку "Форк репозитория".

Теперь нужно создать локальную копию репозитория, отслеживающую основной
репозиторий разработки. Откройте терминал на своём компьютере и выполните
следующие команды:

```
cd ~/Projects
git clone git@bitbucket.org:kris97/cross_journals.git
cd cross_journals
git remote add --track develop --track master upstream git@bitbucket.org:communication_center/cross_journals.git
```

Теперь вы готовы к работе!

## Работа с задачами

Отслеживайте появление новых задач в основном репозитории, которые назначаются
вам. Не забывайте их комментировать при возникновении вопросов по решению задачи.

### Начало работы над задачей

Предположим, вам назначили задачу в основном репозитории. Тогда вам нужно сделать
следующее:

1. Перейти в каталог проекта

        cd ~/Projects/cross_journals

2. Перейти на ветку `develop`

        git checkout develop

3. Получить все изменения из центрального репозитория

        git fetch upstream
        
4. Слить ветку develop из центрального и локального репозиториев

        git merge upstream/develop
        
5. Создать ветку для новой задачи

        git branch feature/new-index-page
        
6. Переключиться на новую ветку

        git checkout feature/new-index-page

7. Установите удаленную ветку для отслеживания относительно текущей ветки

        git push --set-upstream origin feature/new-index-page

8. Начать работу над задачей

### Процесс работы над задачей

Делайте коммиты, как обычно и, по необходимости выполняйте `git push` для отправки
изменений на сервер.

### Окончание работы над задачей

Когда вы решите, что задача решена, пришло самое время создавать *pull request*
(запрос на слияние вашей ветки решения задачи с веткой разработки основного репозитория).
Откройте страницу вашего репозитория на bitbucket и нажмите на кнопку "Создать pull-запрос"
в боковом меню. Данные нужно перенести из вашей ветки, где находится работа по текущей
задаче (в нашем случае `feature/new-index-page`) в ветку `develop` основного репозитория.

Поэтому убедитесь, что слева выбрана ветка `feature/new-index-page`, а справа: репозиторий
`communication_center/cross_journals` и ветка `develop`.

После этого просмотрите изменения внизу экрана и ещё раз проверьте, что отправляете
правильный и работающий код.

Далее введите заголовок, описывающий вашу работу. Он должен быть примерно следующего
формата:

`Переработка главной страницы (closes #15)`

Обратите внимание на **`(closes #15)`**. Это ключевые слова для *bitbucket*, которые
"говорят" ему автоматически закрыть задачу *#15* после принятия *pull request-а*

Возможны также следующие автоматические действия и ключевые слова, которые помогают
связывать задачи и выполнять по ним автоматические действия

![issues actions](http://storage5.static.itmages.ru/i/17/0502/h_1493729356_1687401_ae604e5744.png "Действия по задачам")

Если внесенные изменения связаны с какими-то задачами в трекере прямо, или косвенно,
**обязательно** отмечайте это в заголовке *pull request-а*.

Опционально можете заполнить описание.

Если вы не планируете использовать ветку `feature/new-index-page` после закрытия
*pull request-а*, то поставьте галочку на пункте "Закрыть ветка". В общем случае это
рекомендуемое действие.

После создания запроса на слияние, отслеживайте приходящие по электронной почте
уведомления о изменениях и можете приступать к работе над другой задачей.

Далее возможны три варианта действий. Первый: если с кодом всё в порядке, и он подходит,
то *pull request* принимают и он сливается с веткой `develop` основного репозитория.
В таком случае, вам остаётся только получить коммит слияния и удалить свою ветку
разработки.
```
git checkout develop
git fetch upstream
git merge upstream/develop
git branch -d feature/new-index-page
```
Второй вариант: в комментариях к запросу на слияние вас просят
что-то исправить в самом *pull request-е*. Тогда вы можете его просто отредактировать.
Далее, если с кодом всё в порядке, то действуйте по действиям в первом варианте.

Третий вариант: в коде содержатся ошибки и *pull request* отклоняется. Тогда нужно
сделать коммиты исправляющие замечания в ветку `feature/new-index-page` и, после
окончания "работы над ошибками", создать новый *pull request*.

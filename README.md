# BeautyCity
https://t.me/BeautyCityBot  
@BeautyCityBot  

Это телеграм бот студии BeautyCity для администрирования записи посетителей


## Переменные окружения

Часть настроек проекта берётся из переменных окружения.  
Чтобы их определить, создайте файл `.env` рядом с `manage.py` и запишите туда данные в таком формате: `ПЕРЕМЕННАЯ = значение`:  
- `BOT_TOKEN = 'токен Вашего бота от Telegram'`. [Инструкция, как создать бота.](https://core.telegram.org/bots/features#botfather)  
- `PAYMENT_TOKEN = 'платежный токен Вашего бота от Telegram'`. [Инструкция, как создать платежный токен.](https://habr.com/ru/companies/selectel/articles/729856/)  

- `SECRET_KEY` — секретный ключ проекта в Django. Например: `erofheronoirenfoernfx49389f43xf3984xf9384`.  
- `DEBUG` — дебаг-режим. Поставьте `True`, чтобы увидеть отладочную информацию в случае ошибки. Выключается значением `False`.  
- `ALLOWED_HOSTS` — по умолчанию: localhost, 127.0.0.1. [документация Django](https://docs.djangoproject.com/en/3.1/ref/settings/#allowed-hosts).  
- `DJANGO_SETTINGS_MODULE = 'bot_beautycity.settings'` 
- `STATIC_ROOT` - папка для сбора статики сайта при размещении на сервере, например "assets". Нельзя задавать "static".  
- `CSRF_TRUSTED_ORIGINS = http://subdomen.domen.com` - домен/субдомен сайта.  

Для запуска проекта следующие настройки менять не требуется, значения проставлены для деплоя.  
- `SECURE_HSTS_SECONDS = 10`  
- `SESSION_COOKIE_SECURE = True`  
- `CSRF_COOKIE_SECURE = True`  
- `SECURE_HSTS_PRELOAD = True`  
- `SECURE_HSTS_INCLUDE_SUBDOMAINS = True`  
- `SECURE_SSL_REDIRECT = True`  
[документация по настройкам Django Deployment checklist](https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/).  


## Установка и запуск
Для запуска у вас уже должен быть установлен Python не ниже 3-й версии.  

- Скачайте код
- Создайте файл с переменными окружения.
- Установите зависимости командой `pip install -r requirements.txt`
- Создайте файл базы данных и примените все миграции - командой `python manage.py migrate`
- Запустите бота - командой `python main.py`

## Администрирование

- Для регистрации администратора сайта введите команду `python manage.py createsuperuser`,  
    после чего введите выбранный вами логин, e-mail и пароль администратора (2 раза).  
- При вводе пароля символы не отображаются. Ввод завершается нажатием Enter.  
- Затем запустите сервер для администрирования командой `python manage.py runserver`
- Перейдите по адресу http://127.0.0.1:8000/admin
- Используйте данные для авторизации (Username: Password:, введенные чуть ранее)


## Панель администратора
Перед запуском бота необходимо 
Главное - не забываейте расписать график работы специалистов с помощью кнопок  вверху справа в разделе Schedules:  
`SCHEDULE NEXT DAY` - расписание на следующий после имеющегося последнего в графике дня (даже при наличии только одной записи!!!).  
`PAINT TOMORROW` - расписать завтрашний день.  
`PAINT TODAY` - расписать сегодняшний день.  
При создании расписания уже имеющиеся записи сохраняются.    

Основной вид раздела расписаний (Schedules):  



## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).
 
# Информация по проекту
[Сайт](https://nti.offsound.ru/)

[API](https://api.offsound.ru/admin/warehouse/item/)

[БД Склада](https://api.offsound.ru/admin/warehouse/item/)

[Администрирование](https://api.offsound.ru/admin/)

[Смена пароля](https://api.offsound.ru/password_reset/)

[CURD Endpoint для автоматизации](https://api.offsound.ru/item/)

[Загрузка xlsx расписания](https://api.offsound.ru/item/upload_timetable/)

Пользователь должен иметь разрешение для записи, администратор имеет все праа без явного их указания

После регистрации пользователь может только просматривать данные

Файл [factory_controller.py](https://github.com/de1ay/nti2021-api/blob/master/factory_controller.py) отвечает за управление конвеером в FactoryIO

Стриминг через OBS на nginx-rtmp который преобразует в HLS для хостинга

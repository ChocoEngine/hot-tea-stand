# ESP32-C6 N8: диагностическая Zigbee-лампа для SprutHub

Проект для ESP-IDF **5.3.2**, ESP Zigbee SDK **1.6.x** и ESP32-C6 с Flash 8 МБ.
Используется поддерживаемая LTS-ветка SDK 1.x для сравнения с Arduino; SDK 2.x имеет другой API и сюда не подставляется.
Зависимости загружает IDF Component Manager. После первой успешной сборки сохраните dependencies.lock для воспроизводимости.

## Поведение

- Zigbee End Device, endpoint 10, HA On/Off Light (0x0100).
- Производитель Espressif, модель ZBLightBulb; строки сохранены как в Arduino-тесте.
- Поиск подключения на канале 25, повтор после неудачи.
- В журнале: события Zigbee, успешное подключение с PAN ID/адресом/каналом, команды On/Off.
- Лампа виртуальная: GPIO нагрузки и встроенный RGB не управляются.
- BOOT (GPIO9), удерживаемая 3 секунды во время работы, сбрасывает Zigbee-привязку и перезапускает плату.
- Привязка сохраняется при обычном перезапуске.

## Открытие в VS Code

1. Установите официальное расширение **ESP-IDF** от Espressif Systems.
2. Установите/выберите **ESP-IDF 5.3.2** средствами расширения.
3. Откройте эту папку (с корневым CMakeLists.txt).
4. Запустите команду **ESP-IDF: Open ESP-IDF Terminal**.
5. Подключите левый USB-C **CH343**, выберите его последовательный порт.

## Сборка и первая прошивка

В терминале ESP-IDF, из папки проекта:

```sh
idf.py set-target esp32c6
idf.py build
idf.py -p /dev/cu.usbmodem5B3E0587871 erase-flash
idf.py -p /dev/cu.usbmodem5B3E0587871 flash monitor
```

Порт приведён из прежнего лога, он может измениться. Узнать доступные порты на macOS:

```sh
ls /dev/cu.*
```

**erase-flash нужен только при первом переходе с Arduino на эту разметку. Он удаляет всю прошивку и сохранённые данные платы, включая Zigbee-привязку.** Последующие обновления: `idf.py -p ПОРТ flash monitor` без стирания.
Закройте Serial Monitor Arduino IDE перед прошивкой. Выход из IDF Monitor: Ctrl+].

Если автоматический вход в загрузчик не работает: зажмите BOOT, нажмите и отпустите RST, отпустите BOOT и повторите flash. После прошивки нажмите RST при необходимости.

## Сопряжение

1. В SprutHub включите поиск на ZigBee_1.
2. На работающей плате удерживайте BOOT 3 секунды (не при подаче питания).
3. Дождитесь `Joined network successfully`.
4. Если вновь `Network steering was not successful`, сохраните полный вывод от `TEST-IDF-1` за 60 секунд и журнал хаба за то же время.

ESP_FAIL остаётся общим кодом: проект выводит доступные события SDK, но не является радиосниффером и не гарантирует раскрытие причины отказа. Для представления подключившейся лампы в интерфейсе SprutHub может понадобиться шаблон.

Канал меняется в main/esp_zb_light.h, ESP_ZB_PRIMARY_CHANNEL_MASK. Разметка включает zb_storage и zb_fct. Занята только часть 8 МБ; OTA в этом тесте нет.

## Проверка и источники

Структура проекта, API по заголовкам SDK и отсутствие пересечений разделов проверены. **Сборка и запуск на плате не проверены: ESP-IDF в среде подготовки не установлен.**

Основано на примере Espressif HA_on_off_light (CC0-1.0):
https://github.com/espressif/esp-zigbee-sdk/tree/release/v1.0/examples/esp_zigbee_HA_sample/HA_on_off_light

Совместимость ESP-IDF 5.3.2 рекомендована в README выбранной ветки:
https://github.com/espressif/esp-zigbee-sdk/tree/release/v1.0

Библиотеки esp-zigbee-lib и esp-zboss-lib имеют собственные лицензии; см. загружаемые компоненты.

## Если конфигуратор выбрал ESP-IDF 6.1 или target esp32

Этот проект использует API Zigbee SDK 1.x и требует ESP-IDF 5.3.x (от 5.3.2). Удалять ограничение в idf_component.yml нельзя: это не перенос на SDK 2.x.

В палитре VS Code (Cmd+Shift+P):
1. ESP-IDF: Open ESP-IDF Installation Manager — установите ESP-IDF 5.3.2 для esp32c6 рядом с 6.1.
2. ESP-IDF: Select Current ESP-IDF Version — выберите установленную 5.3.2.
3. ESP-IDF: Set Espressif Device Target — esp32c6.
4. Откройте новый ESP-IDF Terminal и выполните `idf.py --version`, затем `idf.py set-target esp32c6` и `idf.py build`.

Если старый каталог build мешает set-target, переименуйте его в build-old, сохранив для диагностики. Корневой CMakeLists.txt явно задаёт esp32c6; PROJECT_VER задан независимо от наличия коммитов Git.

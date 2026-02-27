# Agro GIS Desktop

Desktop GIS-приложение на Python (PySide6 + GeoPandas) для загрузки карты из `.reg` и точек из `.vbc`, с отображением слоёв, легенды и базовой навигацией.

## Выбор рендеринга карты

Использован **matplotlib FigureCanvasQTAgg**, встроенный в PySide6. Причины:
- нативная интеграция в desktop UI без браузерного движка;
- прямой контроль над стилями векторных слоёв GeoPandas;
- проще реализовать pan/zoom и отображение координат курсора в статус-баре.

## Установка

```bash
pip install -r requirements.txt
```

## Запуск

```bash
python main.py
```

## Формат `.reg`

Поддерживается стратегия по очереди:

1. WKT:
```text
POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))
```

2. Bounding box:
```text
10,20,30,40
```

3. GeoJSON-подобный JSON:
```json
{"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"Point","coordinates":[37.6,55.7]},"properties":{"id":1}}]}
```

4. CSV координат полигона:
```text
30,10
40,40
20,40
10,20
30,10
```

> Если первая непустая строка содержит `Windows Registry Editor`, файл считается экспортом реестра Windows и отклоняется.

## Формат `.vbc`

Ожидаемый вид:
```text
lat, lon, value1, value2
```

- Комментарии `#...` и пустые строки пропускаются.
- Разделители: `,`, `;`, tab, пробел.
- Проверка диапазонов: `lat [-90, 90]`, `lon [-180, 180]`.
- Невалидные строки логируются на `WARNING` и пропускаются.

## Кодировки

Автодетект через `charset-normalizer`.

Fallback-цепочка при низкой уверенности: `UTF-8 -> CP1251 -> CP866 -> Latin-1`.

BOM обрабатывается прозрачно (`UTF-8 BOM`, `UTF-16 LE/BE`).

Если кодировку определить не удалось, генерируется `EncodingDetectionError`, а UI предлагает ручной выбор:
`UTF-8`, `CP1251`, `CP866`, `Latin-1`, `UTF-16`.

## Тесты

```bash
pytest tests/ -v
```

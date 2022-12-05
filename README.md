# Модель
## Исходники и предобработанные данные хранятся в ./storage/data
## Предобработка данных
файл myapp/model/analysis/preprocessing.py

## Определение топа слов
файл myapp/model/analysis/trend_detection.py

## Тестовые версии разных способов посчитать тренды
myapp/model/analysis/rate_growing.py

## Чтобы запустить парсинг данных, обработку и все такое 
запусти файл myapp/model/pipeline.py
Можешь добавить любой тг канал или группу вк (формат там в примерах посмотришь),
для этого поменяй список с источниками в самом конце файла pipeline.py в исполняемой части (где конструкция if __ name __ == "__ main __")

## .

# Trend Analysis Bot

## Description
@TrendAnalysisBot

It is bot for telegram, that parses data from telegram channels, VK groups and websites, process it/ The result is pdf file with trending topic and graphs with history of their behaviour.

## Installation
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install required libraries.

```bash
pip install -r requirements.txt
```
Download russian language model for spacy

```bash
python3 -m spacy download ru_core_news_lg
```
Install [MongoDB](https://www.mongodb.com/docs/manual/administration/install-community/)

Start MongoDB 
```bash
sudo systemctl start mongod
```

Intsall dependancy for PDF converter
```bash
sudo apt-get install wkhtmltopdf
```

Run setup.py to find all required packages

To start bot run bot.py

## Usage

To grand access to bot to new users put their telegram nicknames in file users_whitelist.txt

To drop database run migration.py
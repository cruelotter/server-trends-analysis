# Trend Analysis Bot

## Description
[@TrendAnalysisBot](https://t.me//TrendAnalysisBot)

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
python -m venv bot_venv
source bot_venv/bin/activate
```

Run setup.py to find all required packages
```bash
python setup.py install
```

To start bot run bot.py
```bash
python analysisbot/bot/bot.py
```

## Usage

To grand access to bot to new users put their telegram nicknames in file users_whitelist.txt

To drop database run migration.py

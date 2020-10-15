# neko-chan-telebot

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/ksdfg/neko-chan-telebot/graphs/commit-activity)
![GitHub contributors](https://img.shields.io/github/contributors/ksdfg/neko-chan-telebot)
![GitHub last commit](https://img.shields.io/github/last-commit/ksdfg/neko-chan-telebot)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com) 
![GitHub pull requests](https://img.shields.io/github/issues-pr-raw/ksdfg/neko-chan-telebot) 
![GitHub closed pull requests](https://img.shields.io/github/issues-pr-closed-raw/ksdfg/neko-chan-telebot) 
![GitHub](https://img.shields.io/github/license/ksdfg/neko-chan-telebot)

Updated version of [SkittBot](https://github.com/skittles9823/SkittBot) with some features from 
[skitt_bot](https://github.com/skittles9823/skitt_bot) to work with latest version of python-telegram-bot

## Config

You can set config variables in your environment, store them in a `.env` file in the project root or give them as
commandline arguments while running the bot.

The config variables are as follows :-
- `ADMIN` : The user ID of the person managing the bot
- `TOKEN` : Telegram bot token
- `DATABASE_NAME` : The name of the database you are using
- `DATABASE_URL` : The MongoDB host URI (if not given, bot will try to connect to local MongoDB instance at default port)
- `WEBHOOK_URL` : The URL your webhook should connect to (Default value is `False`, which will disable webhook)
- `PORT` : Port to use for your webhooks (Default value is `80`)
- `LOAD` : Space separated list of modules (`.py` file name) you would like to load (Default value is `False`, which will just load all modules)
- `NO_LOAD` : Space separated list of modules (`.py` file name) you would like NOT to load (Default value is `False`, which will not skip any modules
- `SUPERUSERS` : Space separated list of user IDs for which some exceptions won't work

## Running the bot

To run the bot, simply run
```shell script
python -m telebot
```

In case you want to deploy the bot on Heroku, the Procfile and runtime.txt is given in the repo. For optimal usage do
set the `WEBHOOK_URL` to the heroku application URL (generally https://app_name.herokuapp.com).

## Note

For the first 70 commits or so, I didn't know that the concept of co-authorship existed.... so while the base logic is 
the same as the above mentioned repositories with some changes that I thought were needed, the commit authorship for 
those is shown as mine. Now there's a lot of stuff within those 70 commits that actually are my own idea (like the 
`exceptions` and `nhentai` modules, as well as the mongodb schemas for everything) and it would honestly be a pain to go 
through all 70 commits and figure out which to amend and change authorship of to add co-authorship to 
[Rhyse Simpson](https://github.com/skittles9823)

I got to talk to him on telegram and he said it was kinda OK to let the current history be and I can add him as 
co-author on all future commits where I'm taking his code and either just updating it to work with latest version of 
`python-telegram-bot` or editing it as I see fit. So please don't flame me too much for essentially kanging those 
entire projects :P This bot was kinda meant more for me to have everything I want in a single place and on the way 
somehow became about wanting to kick @NotAMemeBot from a group I'm on (yeah, I'm kinda irrational that way).

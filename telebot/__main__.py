from mongoengine import connect

from telebot import updater, config, application
from telebot.modules import imported_mods, bot_commands

# log all imported modules
print("Imported modules :", ", ".join(sorted(mod.__mod_name__ for mod in imported_mods.values())))

if __name__ == "__main__":
    # set bot commands to be displayed
    print("Commands set :", *(cmd.command for cmd in bot_commands))
    await updater.bot.set_my_commands(bot_commands)

    # connect to database
    connect(config.DATABASE_NAME, "default", host=config.DATABASE_URL)

    # start bot
    if config.WEBHOOK_URL:
        await updater.bot.delete_webhook()  # in case there's one up
        await application.run_webhook(
            listen="0.0.0.0", port=config.PORT, url_path=config.TOKEN, webhook_url=config.WEBHOOK_URL + config.TOKEN
        )
    else:
        application.start_polling()

    print("neko chan go nyan nyan")
    updater.idle()

import importlib

from telebot import updater, config
from telebot.modules import ALL_MODULES

# Import all modules
IMPORTED = set()
for module_name in ALL_MODULES:
    if (config.LOAD and module_name not in config.LOAD) or (config.NO_LOAD and module_name in config.NO_LOAD):
        continue

    imported_module = importlib.import_module("telebot.modules." + module_name)
    IMPORTED.add(module_name)

print("Imported modules :", sorted(IMPORTED), "\n")

if __name__ == "__main__":
    # start bot
    if config.WEBHOOK_URL:
        updater.start_webhook(listen="0.0.0.0", port=config.PORT, url_path=config.TOKEN)
        updater.bot.set_webhook(url=config.WEBHOOK_URL + config.TOKEN)

    else:
        updater.start_polling()

    print("neko chan go nyan nyan")
    print("------------------------------------")
    updater.idle()

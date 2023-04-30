from src.bot import BotClass
from src import config


def main():
    bot = BotClass.BotClass(token=config.BOT_TOKEN)
    bot.infinity_polling()


if __name__ == "__main__":
    main()

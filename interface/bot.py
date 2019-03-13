import const.stat as ic
import telegram # python-telegram-bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


class TelegramBot:
    def __init__(self, name, token):
        self.core = telegram.Bot(token)
        self.updater = Updater(token=token)
        self.dispatcher = self.updater.dispatcher

        self.text_print_handler = MessageHandler(Filters.text, self.print_message)
        self.dispatcher.add_handler(self.text_print_handler)

        # 013 : me, 535 : song
        self.id = ic.telegram["chat_id"]
        self.name = name

    def print_message(self, bot, text):
        print(bot)
        print(text)

    def send_message(self, text):
        for one_id in self.id:
            self.core.sendMessage(chat_id=one_id, text=text)

    def stop(self):
        self.updater.start_polling()
        self.updater.dispatcher.stop()
        self.updater.job_queue.stop()
        self.updater.stop()


class BotSmwj(TelegramBot):
    def __init__(self, qobject):
        # parent object
        self.par = qobject

        self.token = ic.telegram["token"]
        TelegramBot.__init__(self, 'smwj', self.token)

        self.add_handler("accnt", self.send_accnt_items)
        self.add_handler("startat", self.set_start_time)
        self.add_handler("shutdown", self.shut_down)
        self.updater.stop()

    def add_handler(self, cmd, func):
        self.dispatcher.add_handler(CommandHandler(cmd, func))

    def send_accnt_items(self, bot, update):
        self.par.logger.info("show account command is accepted")

        price = self.par.kiwoom.price
        buy_price = self.par.kiwoom.buy_price
        item_names = self.par.kiwoom.item_names
        buy_tot = self.par.kiwoom.buy_tot

        for key, value in price.items():
            # filter today's sold item
            if int(buy_price[key]) <= 0:
                continue

            rate = round((int(value[-1]) - int(buy_price[key])) / int(buy_price[key]), 2)

            self.send_message(str(item_names[key]) + " | 현재가 : " + str(value[-1]) + ", 매입가 : " +
                              str(buy_price[key]) + ", 수익률 : " + str(rate) + ", 매입총액 : " + str(buy_tot[key]))

    def set_start_time(self, bot, update):

        st = update.message.text
        if " " in st:
            self.par.start_time = int(st.split(" ")[1] + "00")
            self.send_message("starting time is updated to : " + str(self.par.start_time))

        self.par.logger.info("starting time is updated to : " + str(self.par.start_time))

    def shut_down(self, bot, update):
        self.par.logger.info("shutdown command is accepted")

        self.par.shut_down()

    def start(self):
        self.par.logger.info("chatbot started")
        self.updater.start_polling()
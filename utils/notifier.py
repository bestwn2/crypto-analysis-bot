# utils/notifier.py
import telegram
import configparser

class TelegramNotifier:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config/config.ini', encoding='utf-8')
        try:
            token = config.get('TELEGRAM', 'BOT_TOKEN')
            self.chat_id = config.get('TELEGRAM', 'CHAT_ID')
            self.bot = telegram.Bot(token=token)
        except (configparser.NoSectionError, configparser.NoOptionError):
            print("⚠️ زانیاری تێلیگرام لە config.ini نەدۆزرایەوە. ئاگادارکردنەوە کار ناکات.")
            self.bot = None

    def send_message(self, message):
        if self.bot and self.chat_id:
            try:
                self.bot.send_message(chat_id=self.chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN)
                return True
            except Exception as e:
                print(f"❌ هەڵە لە ناردنی پەیامی تێلیگرام: {e}")
                return False
        return False
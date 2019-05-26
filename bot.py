import logging
import tokens
import sys
# import dataset
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ParseMode
from helpers import * # getTimeAgo
#Python Reddit API Wrapper
import praw

# Logger setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    stream=sys.stdout)

logger = logging.getLogger(__name__)

# Create reddit wrapper object
reddit = praw.Reddit(client_id = tokens.client_id,
                    client_secret = tokens.client_secret,
                    user_agent = tokens.user_agent)

class RedditBot():
    """
    Creates and mantains connection with Telegram.
    Provides content from Reddit through Telegram chat.

    Handles multiple commands (e.g. \start).
    Subreddits can be chosen using commands.
    """

    def __init__(self):
        # Create useful objects
        updater = Updater(token=tokens.telegram_token, use_context=True)
        dispatcher = updater.dispatcher

        # Add Handlers
        # Handlers check the update in the order they were added
        # (So the errors etc. should be last)
        dispatcher.add_handler(CommandHandler('start', self.start))
        dispatcher.add_handler(CommandHandler('help', self.help))
        dispatcher.add_handler(CommandHandler('stats', self.stats))
        # dispatcher.add_handler(MessageHandler(Filters.text, self.echo))
        dispatcher.add_handler(MessageHandler(Filters.text, self.fetch))
        # dispatcher.add_error_handler(ErrorHandler(self.error_callback))
        dispatcher.add_handler(MessageHandler(Filters.command, self.unknown))


        # Initial values of parameters
        self.message = ''
        self.chat_id = None
        self.user_id = None
        self.subreddit = None
        self.submission = None

        # Start the bot
        updater.start_polling()
        logger.info("RedditBot started polling.")

    # Commands actions
    def start(self, update, context):
        context.bot.send_message(chat_id=update.message.chat_id, text="Hello. I'm a bot, please talk to me!")

    def help(self, update, context):
        context.bot.send_message(chat_id=update.message.chat_id, text="Hello. These are the available options:")

    def echo(self, update, context):
        logger.info("Received message: '%s' (echo)", update.message.text)
        logger.info(update)
        context.bot.send_message(chat_id=update.message.chat_id, text=update.message.text)

    def stats(self):
        pass

    def unknown(self, update, context):
        logger.info("Received Unknown command: '%s'", update.message.text)
        context.bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")

    def fetch(self, update, context):
        logger.info("Received message: '%s' (fetch)", update.message.text)

        self.set_message(update)
        self.set_chat_id(update)
        self.set_user_id(update)
        self.set_subreddit(update)

        if self.subreddit is not None:
            self.get_submission()
            self.show_submission(update, context)

    
    def error_callback(self, update, context):
        logger.warning('Update "%s" caused error "%s"', update, context.error)

    def set_message(self, update):
        self.message = update.message.text

    def set_chat_id(self, update):
        self.chat_id = update.message.chat_id

    def set_user_id(self, update):
        self.user_id = update.message.from_user.id

    def set_subreddit(self, update):
        self.subreddit = update.message.text

    def get_submission(self):
        # self.submission = reddit.subreddit(self.subreddit).hot(limit=1).submission
        for submission in reddit.subreddit(self.subreddit).hot(limit=1):
            self.submission = submission


        logger.info("Fetched from /r/%s" % self.subreddit)

    def show_submission(self, update, context):

        def make_snippet():
            url = self.submission.permalink.replace('www.reddit.', 'm.reddit.')
            comments = len(self.submission.comments)
            timestamp = getTimeAgo(self.submission.created_utc)
            return '<a href="old.reddit.com/%s">%d score, %d comments, %s</a>' % \
                        (url, self.submission.score, comments, timestamp)

        text = "[%s](%s)" % (self.submission.title, self.submission.url)
        context.bot.sendMessage(chat_id=self.chat_id,
                        text=text,
                        parse_mode=ParseMode.MARKDOWN)

        # send short link to reddit, no preview. also keyboard to continue
        context.bot.sendMessage(chat_id=self.chat_id,
                        text=make_snippet(),
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True)


        logger.info("Shown https://redd.it/%s" % self.submission.id)

    # def hello(bot, update):
    # 	update.message.reply_text(
    # 		'Hello {}'.format(update.message.from_user.first_name))

    # start_handler = CommandHandler('start', start)
    # hello_handler = CommandHandler('hello', hello)

    # updater = Updater(token=tokens.telegram_token, use_context=True)
    # dispatcher = updater.dispatcher

    # dispatcher.add_handler(hello_handler)
    # dispatcher.add_handler(start_handler)


# updater.idle()


if __name__ == "__main__":
        RedditBot()
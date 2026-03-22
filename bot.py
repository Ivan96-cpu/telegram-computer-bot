import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
TOKEN = '8617492333:AAExotDqmxnKfg1lVflpXOStX1PNvWewFF0'
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Привет! Я бот для сборки компьютера.\n'
        'Используй команду /help для списка команд.'
)
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Доступные команды:\n'
        '/start - начать работу\n'
        '/build - начать сборку компьютера\n'
        '/help - показать это сообщение'
)
async def build(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Давай соберём компьютер!\n'
        'Введите ваш бюджет (в рублях):'
)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_id = update.effective_user.id
     await update.message.reply_text(f'Вы написали: {user_message}')
def main():
     application = Application.builder().token(TOKEN).build()
     application.add_handler(CommandHandler("start", start))
     application.add_handler(CommandHandler("help", help_command))
     application.add_handler(CommandHandler("build", build))
     application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
     application.run_polling()
if __name__ == '__main__':
    main()

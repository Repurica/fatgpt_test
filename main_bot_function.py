import logging
import telegram
from telegram import Update,InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, InlineQueryHandler
import pathlib

#log
# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )

#receive&reply message
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="I'm a bot, please talk to me!"
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text=update.message.text
    #reply with text
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=text)

    #reply with file
    # await context.bot.send_document(
    #     chat_id=update.effective_chat.id,
    #     document="1.html"
    # )


    #reply with photo
    # with open("./image1.webp", 'rb') as f:
    #     file=f.read()

    # await context.bot.send_photo(chat_id=update.effective_chat.id,
    #     photo="image1.webp")

#reply inline query
async def inline_caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    print(query)
    if not query:
        return
    results = []
    results.append(
        InlineQueryResultArticle(
            id=query,
            title='Caps',
            input_message_content=InputTextMessageContent(query)
        )
    )
    print(results)
    await context.bot.answer_inline_query(update.inline_query.id, results)

#receive file
async def downloader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file=await context.bot.get_file(update.message.document.file_id)
    await file.download_to_drive(update.message.document.file_name)
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="done")



#wrap up
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="Sorry, I didn't understand that command.")




if __name__ == '__main__':
    #bot token
    application = ApplicationBuilder().token('6625209100:AAHubzFHR4rpc8CNZCfPgChjWQdq3M3LHIE').build()
    
    #load bot handler 
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    

    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    application.add_handler(echo_handler)

    inline_caps_handler = InlineQueryHandler(inline_caps)
    application.add_handler(inline_caps_handler)

    file_handler=MessageHandler(filters.Document.ALL, downloader)
    application.add_handler(file_handler)




    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    #launch
    print("running")
    application.run_polling()
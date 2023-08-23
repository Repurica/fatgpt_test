
import logging
import telegram
from telegram import Update,InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ConversationHandler,ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, InlineQueryHandler
import pathlib
import os
import shutil
import requests


#log
# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )

#start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="this is FATGPT, plz use /upload to upload files, or it will not be accepted"
    )


# to check if bot running
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text=update.message.text
    #reply with text
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=text)

    #reply with file
    # await context.bot.send_document(
    #     chat_id=update.effective_chat.id,``
    #     document="1.html"
    # )


    #reply with photo
    # with open("./image1.webp", 'rb') as f:
    #     file=f.read()

    # await context.bot.send_photo(chat_id=update.effective_chat.id,
    #     photo="image1.webp")

#reply inline query
# async def inline_caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     query = update.inline_query.query
#     print(query)
#     if not query:
#         return
#     results = []
#     results.append(
#         InlineQueryResultArticle(
#             id=query,
#             title='Caps',
#             input_message_content=InputTextMessageContent(query)
#         )
#     )
#     print(results)
#     await context.bot.answer_inline_query(update.inline_query.id, results)
    # inline_caps_handler = InlineQueryHandler(inline_caps)
    # application.add_handler(inline_caps_handler)


#receive file
async def downloader(update: Update, context: ContextTypes.DEFAULT_TYPE):

    file=await context.bot.get_file(update.message.document.file_id)


    folder_name=update.message.from_user.username

    await file.download_to_drive(folder_name+"/"+update.message.document.file_name)
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="received, when finish enter /finish, cancel enter /cancel")

#init upload
async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    folder_name=update.message.from_user.username

    if(os.path.exists(folder_name)):
        shutil.rmtree(folder_name)
    os.mkdir(folder_name)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="ok plz send the files, when finish enter /finish, cancel enter /cancel"
    )
    return downloader
#end conversation
async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE):


    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="finished file uploading let me process"
    )
    return ConversationHandler.END

# remove the folder to cancel upload
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    folder_name=update.message.from_user.username
    
    if(os.path.exists(folder_name)):
        shutil.rmtree(folder_name)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="cancelled plz use /upload again"
    )
    return ConversationHandler.END


# send file without /upload
async def send_file_without_upload_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="plz use /upload to start an upload"
    )



async def idea(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["next_offset"]=0
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="the next message will be used to query for articles!"
    )
    return query



async def query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if("query" not in context.user_data):
        context.user_data["query"]=update.message.text

    URL ="http://api.semanticscholar.org/graph/v1/paper/search"
    # offset: skip first 10 result, limit: limit the number of records output, fields
    PARAMS = {'query':context.user_data["query"],"offset":context.user_data["next_offset"],"fields":"title,authors"}
    r=requests.get(url=URL, params=PARAMS)
    data=r.json()
    output=""
    print(data["data"])
    for paper in data["data"]:
        output+="<b>"+paper["title"]+"</b>\n\nPaper ID: "+paper["paperId"]+"\n\nAuthors:\n"

        for author in paper["authors"]:
            output+=author["name"]+"\n"
        output+="\n\n"

    output+="here are "+str(context.user_data["next_offset"]+1)+" - "+str(context.user_data["next_offset"]+10)+" records, /next for the next 10, /query_finish to stop"
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=output,
        parse_mode="HTML"
    )
    return next

async def next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["next_offset"]+=10
    await query(update, context)



async def query_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    del context.user_data["next_offset"]
    del context.user_data["query"]

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="ok here are your files, lmk if it works"
    )
    return ConversationHandler.END






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



    query_handler=ConversationHandler(
        entry_points=[CommandHandler('idea', idea)],
        states={query:[MessageHandler(filters.TEXT & (~filters.COMMAND), query)],
                next:[CommandHandler("next", next)]},
        fallbacks=[CommandHandler('query_finish', query_finish)])
    application.add_handler(query_handler)
 
    # use /upload to start an upload, then upload file as you like, 
    # choose /cancel to remove folders,
    # choose /finish to process the files
    file_reciever_handler=ConversationHandler(
        entry_points=[CommandHandler('upload', upload)],
        states={downloader:[MessageHandler(filters.Document.ALL, downloader)]},
        fallbacks=[CommandHandler('finish', finish),CommandHandler('cancel', cancel)])
    application.add_handler(file_reciever_handler)

    # must come after the file_reciever_handler!!!
    send_file_without_upload_cmd_handler=MessageHandler(filters.Document.ALL, send_file_without_upload_cmd)
    application.add_handler(send_file_without_upload_cmd_handler)

    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    application.add_handler(echo_handler)
    # must come after everything
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    #launch
    print("running")
    application.run_polling()
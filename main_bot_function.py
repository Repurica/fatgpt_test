
import logging
import telegram
from telegram import InlineKeyboardMarkup,InlineKeyboardButton,Update,InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import CallbackQueryHandler, ConversationHandler,ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, InlineQueryHandler
import pathlib
import os
import shutil
import requests

import backend_api


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



async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text=update.message.text
    #reply with text
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=text
        )


# to check if bot running
async def chat_with_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="hi plz enter message"
        )
    return chat
    # text=update.message.text
    # #reply with text
    # await context.bot.send_message(
    #     chat_id=update.effective_chat.id, 
    #     text=context.user_data["engine"]
    #     )

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
# async def inline_caps(update: Update, `context: ContextTypes.DEFAULT_TYPE):
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


async def refresh_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("context")
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="conversation cleared! start a new one with /chat"
        )
    return ConversationHandler.END

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "context" not in context.user_data:
        reply,chat_context=backend_api.context(update.message.text,"")
    else:
        reply,chat_context=backend_api.context(update.message.text,context.user_data["context"])

    context.user_data["context"]=chat_context
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=reply+"\n\n\nenter text to continue chat, or /refresh_gpt to clear the convo!"
        )

async def engine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Semantic Scholar", callback_data="Semantic Scholar"),
            InlineKeyboardButton("Scopus", callback_data="Scopus"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("plz select one engine", 
                                    reply_markup=reply_markup)

async def engine_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    selection = update.callback_query.data
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=selection
    )
    context.user_data["engine"]=selection
    await update.callback_query.answer()


#receive file
async def downloader(update: Update, context: ContextTypes.DEFAULT_TYPE):

    file=await context.bot.get_file(update.message.document.file_id)


    folder_name=update.message.from_user.username

    
    
    keyboard = [
        [
            InlineKeyboardButton("Finish", callback_data="Finish"),
            InlineKeyboardButton("Cancel", callback_data="Cancel"),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("received, when finish enter /finish, cancel enter /cancel:", reply_markup=reply_markup)
 
    await file.download_to_drive(folder_name+"/"+update.message.document.file_name)
    # await context.bot.send_message(
    #     chat_id=update.effective_chat.id, 
    #     text="received, when finish enter /finish, cancel enter /cancel")

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
    directory=os.getcwd()+"/"+update.callback_query.from_user.username
    
    for filename in os.listdir(directory):
        summary,keywords_dict=backend_api.summarisation(os.path.join(directory, filename))
        keywords_str=""

        for i in keywords_dict["keywords"]:
            keywords_str+=i+", "

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="<b>"+filename+"</b>\n\n"+summary+"\n\n"+"<b>keywords related: </b>\n"+keywords_str[:-2],
            parse_mode="HTML"
        )

    return ConversationHandler.END

# remove the folder to cancel upload
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    folder_name=update.callback_query.from_user.username
    
    if(os.path.exists(folder_name)):
        shutil.rmtree(folder_name)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="cancelled plz use /upload again"
    )
    return ConversationHandler.END



async def file_upload_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query.data
    await update.callback_query.answer()
    
    if(query=="Finish"):
       await finish(update,context)
    elif(query=="Cancel"):
       await cancel(update,context)











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
    print("here")
    if("query" not in context.user_data):
        context.user_data["query"]=update.message.text
    # offset: skip first 10 result, limit: limit the number of records output, fields
    # query':context.user_data["query"] --> the actual query from the next message
    URL ="http://api.semanticscholar.org/graph/v1/paper/search"
    PARAMS = {'query':context.user_data["query"],"offset":context.user_data["next_offset"],"fields":"title","isOpenAccess":"True"}
    r=requests.get(url=URL, params=PARAMS)
    data=r.json()

    # print(context.user_data["query"])
    

    if(data["total"]==0):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="sorry no articles, try /idea and another keywords",
            parse_mode="HTML"
        )
        return ConversationHandler.END

    else:
        output=""
        for paper in data["data"]:
            output+="<b>"+paper["title"]+"</b>\n\nPaper ID: "+paper["paperId"]+"\n\n"

        #jm processing code
        output+="here are your results, /query_finish to stop"
        # await context.bot.send_message(
        #     chat_id=update.effective_chat.id,
        #     text=output,
        #     parse_mode="HTML"
        # )

        keyboard = [
            [
                InlineKeyboardButton("keyword1", callback_data="AI"),
                InlineKeyboardButton("keyword2", callback_data="MCU"),
                InlineKeyboardButton("keyword3", callback_data="SPIDER")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        # await update.message.reply_text(
        #     "received, when finish enter /finish, cancel enter /cancel:",
        #     reply_markup=reply_markup)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=output,
            parse_mode="HTML",
            reply_markup=reply_markup
        )


async def keyword_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyword = update.callback_query.data
    await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="searching <b>"+keyword + "</b> plz wait...",
            parse_mode="HTML"
            )
    await update.callback_query.answer()
    context.user_data["query"]=keyword
    await query(update,context)


async def query_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    del context.user_data["next_offset"]
    del context.user_data["query"]

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="ok here are your files, lmk if it works"
    )
    return ConversationHandler.END



async def reject_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="plz /query_finish before using another command!"
    )


#wrap up
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="Sorry, I didn't understand that command!")



if __name__ == '__main__':
    #bot token
    application = ApplicationBuilder().token('6144918637:AAG5gUtKOtgsz7qjygETGdCFvnVK92wdmks').build()
    
    #load bot handler 






    chat_handler=ConversationHandler(
        entry_points=[CommandHandler("chat",chat_with_gpt)],
        states={chat:[MessageHandler(filters.TEXT & (~filters.COMMAND), chat)]},
        fallbacks=[CommandHandler("refresh_gpt",refresh_gpt)]
    )
    application.add_handler(chat_handler)


# next:[CommandHandler("next", next)]
    query_handler=ConversationHandler(
        entry_points=[CommandHandler('idea', idea)],
        states={query:[MessageHandler(filters.TEXT & (~filters.COMMAND), query),
                       CallbackQueryHandler(keyword_button),
                       CommandHandler('query_finish', query_finish),
                       MessageHandler(filters.TEXT & filters.COMMAND,reject_command)],
                #next:[CommandHandler("next", next)],
              },
        fallbacks=[CommandHandler('query_finish', query_finish)])
    application.add_handler(query_handler)
 
 
    # use /upload to start an upload, then upload file as you like, 
    # choose /cancel to remove folders,
    # choose /finish to process the files
    file_reciever_handler=ConversationHandler(
        entry_points=[CommandHandler('upload', upload)],
        states={downloader:[MessageHandler(filters.Document.ALL, downloader)]},
        fallbacks=[CallbackQueryHandler(file_upload_button)])
    # file_reciever_handler=ConversationHandler(
    #     entry_points=[CommandHandler('upload', upload)],
    #     states={downloader:[MessageHandler(filters.Document.ALL, downloader)]},
    #     fallbacks=[CommandHandler('finish', finish),CommandHandler('cancel', cancel)])
    application.add_handler(file_reciever_handler)

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    # must come after the file_reciever_handler!!!
    send_file_without_upload_cmd_handler=MessageHandler(filters.Document.ALL, send_file_without_upload_cmd)
    application.add_handler(send_file_without_upload_cmd_handler)

    engine_selection_handler=CallbackQueryHandler(engine_selection)
    application.add_handler(engine_selection_handler)
    engine_handler = CommandHandler('engine', engine)
    application.add_handler(engine_handler)

    # must come after everything
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    application.add_handler(echo_handler)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    #launch
    print("running")
    application.run_polling()
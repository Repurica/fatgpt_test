import os
import logging
import openai
import requests
import json
from telegram import Update
from telegram.ext import (
    filters,
    MessageHandler,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# Set logger
# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
# )

# Define OpenAI API key
openai.api_key = "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"
scopusKey = "17abfb9454e405a8ebb7b7e73b1c7695"


# Handle /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm your personal openai bot."
    )


# Generate response
chat_context = {}

# def get_current_weather(location):
    # api_key = "084225f5b4f152362918c7299365548a" 
    # url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}"

    # response = requests.get(url)
    # data = response.json()

    # weather = f"The weather in {location} is {data['weather'][0]['description']} with a temperature of {data['main']['temp']} °C"

    # return json.dumps(weather)

def scopus(topic : str):
    url = "https://api.elsevier.com/content/search/scopus?"
    params = {'query':topic, 'apikey':scopusKey}
    response = requests.get(url, params)
    recs = []
    res_dict = response.json()
    res = res_dict["search-results"]["entry"] #Returns a list of all results

    # print(res)
    # print(res)
    for book in res:
        # print(book)
        titleDOI = []
        if (len(recs)>9):
            break
        if (book.get("prism:doi") and len(recs) < 11):
            titleDOI.append(book["dc:title"])
            # print(book["dc:title"])
            # titleDOI.append(book["prism:doi"])
            recs.append(titleDOI)

    # print(type(res))
    return recs




async def generate_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text

    global chat_context
    if not chat_context:
        chat_context = {
            "messages": [
                {"role": "system", "content": "A model that intakes a user's broad academic or professional interest, refines it into a focused area of study or project topic, and then provides personalized resources and a learning pathway tailored to their unique goals. For instance, if a user mentions they're a Biology student but wishes to delve into data analytics, the model will offer resources on bioinformatics and a suggested learning journey. Do not provide any links."},
                {"role": "user", "content": str(message)}
            ],
            "functions": [
                    {
                        "name": "scopus",
                        "description": "Search for papers on a given topic",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "topic": {
                                    "type": "string"
                                },
                            },
                            "required": ["topic"]
                    }
                    }
            ]
        }
    else:
        chat_context["messages"].append({"role": "user", "content": str(message)})

    # write code to do some basic logging for debugging
    print('\n')
    print(chat_context)
    print('\n')
    response = openai.ChatCompletion.create(
        model="ft:gpt-3.5-turbo-0613:smulib::7rod2SNU",
        messages=chat_context['messages'],
        # functions=chat_context['functions']
    )

    response_message = response["choices"][0]["message"]["content"]
    # if not response_message:
    #     response_message = "Our brains are on fire now. Please try again later."

    chat_context["messages"].append({"role": "assistant", "content": str(response_message)})

    if response["choices"][0]["message"].get("function_call"):
        available_functions = {
            "scopus": scopus,
        }
        function_name =  response["choices"][0]["message"]["function_call"]["name"]
        function_to_call = available_functions[function_name]
        function_args = json.loads( response["choices"][0]["message"]["function_call"]["arguments"])
        function_response = function_to_call(
            topic=function_args.get("topic")
        )
        chat_context["messages"].append({"role": "assistant", "content": str(message)})
        chat_context["messages"].append(
            {
                "role": "function",
                "name": function_name,
                "content": str(function_response),
            }
        ) 
        response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=chat_context['messages'],
            functions=chat_context['functions']
        ) 
        response_message = response["choices"][0]["message"]["content"]

    # Send message back
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response_message)


# Handle unknow command
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Sorry, I don't understand your command."
    )


if __name__ == "__main__":
    # Set Telegram bot
    application = (
        ApplicationBuilder()
        .token("6647857459:AAEAMEBPW_nkafpRrOvRr3udUJEKkFcIvlg")
        .build()
    )

    # /start
    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)

    # Message handler
    generate_response_handler = MessageHandler(
        filters.TEXT & (~filters.COMMAND), generate_response
    )
    application.add_handler(generate_response_handler)

    # Unknown command handler
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    # Start bot
    application.run_polling()

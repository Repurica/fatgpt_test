import os
import logging
import openai
import requests
from telegram import Update
from telegram.ext import (
    filters,
    MessageHandler,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# Set logger
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Define OpenAI API key
openai.api_key = "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"


# Handle /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm your personal openai bot."
    )


# Generate response
chat_context = {}

def get_weather(location):
    api_key = "084225f5b4f152362918c7299365548a" 
    url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}"

    response = requests.get(url)
    data = response.json()

    weather = f"The weather in {location} is {data['weather'][0]['description']} with a temperature of {data['main']['temp']} °C"

    return weather

async def generate_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text

    global chat_context
    if not chat_context:
        chat_context = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": message}
            ],
            "functions": [
                {
                "name": "get_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"]
                    }
                    },
                    "required": ["location"]
                }
                }
        ]
        }
    else:
        chat_context["messages"].append({"role": "user", "content": message})

    # Call OpenAI API
    print('\n\n')
    # print(chat_context['functions'])
    print(' CALLING OPENAI ')
    print('\n\n')
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=chat_context['messages'],
        functions=chat_context['functions']
    )
    response_message = response["choices"][0]["message"]
    # response_message = response
    print("Response:", response_message)
    print('\n\n')
    # print(chat_context['functions'])
    print(' CALLING OPENAI END')
    print('\n\n')

    if not response_message:
        response_message = "Hmm, I don't have a response for that"

    # Append response to context
    chat_context["messages"].append({"role": "assistant", "content": response_message})

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

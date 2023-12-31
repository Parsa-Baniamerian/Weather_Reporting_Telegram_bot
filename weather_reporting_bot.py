from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import configparser

# Import Token and keys
config = configparser.ConfigParser()
config.sections()
config.read("./set.conf")
config.sections()
TOKEN = config['BOT']['TOKEN']
BOT_USERNAME = config['BOT']['USERNAME']

BASE_URL: Final = "http://api.openweathermap.org/data/2.5/weather?"
API_KEY = config['API']['API_KEY']


# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! I am a meteorological robot.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("If you want to know about the weather condition of any city, you can send me the name of the city you want in P.V., or mention me in a message in the group and write the name of that city :)")


# Handle Response
def handle_response(city):
    url = BASE_URL + "appid=" + API_KEY + "&q=" + city
    response = requests.get(url).json()

    if response["cod"] == 200:
        def kelvin_to_celsius(kelvin): return kelvin - 273.15
        temp_kelvin = response["main"]["temp"]
        temp_celsius = str(int(kelvin_to_celsius(temp_kelvin)))

        feels_like_kelvin = response["main"]["feels_like"]
        feels_like_celsius = str(int(kelvin_to_celsius(feels_like_kelvin)))

        humidity = str(response["main"]["humidity"])

        description = response["weather"][0]["description"]

        wind_speed = str(round(response["wind"]["speed"], 1))

        result = "🌆 " + city + "\n\n🌡 " + temp_celsius + "°C\n\n" + description + "\n\nHumidity   \t" + humidity + "%" \
            "\n\nWind           " + wind_speed + "km/h" + \
            "\n\nRealFeel     " + feels_like_celsius + "°C"
    else:
        result = "Sorry, I couldn't fetch weather data for " + city
    return result


# Handle Messages
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text: str = update.message.text
    if "@Weather_Land_bot" in text:
        city = text.replace("@Weather_Land_bot", "").strip()
    else:
        city = text.strip()
    result = handle_response(city)

    await update.message.reply_text(result)


# Watch errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


if __name__ == "__main__":
    print("Starting bot")
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_messages))

    # Errors
    app.add_error_handler(error)

    # Check for new messages from user
    print("Polling...")
    app.run_polling(poll_interval=1)

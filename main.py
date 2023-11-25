import json
import logging
import httpx
import requests
from dotenv import load_dotenv
import os

import  os
from telegram import __version__ as TG_VER, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, ReplyKeyboardRemove
from telegram import LabeledPrice, ShippingOption, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PreCheckoutQueryHandler,
    ShippingQueryHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

load_dotenv()
PAYMENT_PROVIDER_TOKEN = os.getenv("PAYMENT_PROVIDER_TOKEN")
token = os.getenv("token")
token_send=os.getenv("token_send")
# token_send="6684790933:AAH3-XTOREngaAjRYWR8SgXgOhkWDqB_KsI";

# PAYMENT_PROVIDER_TOKEN = "6141645565:TEST:e9RP7QEUDOVu2sPPDaYn"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with a button that opens a the web app."""

    await update.message.reply_text(
        "Well come to Yene Delivry Telegram bot.",
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                text="Open YeneDelivery web",
                web_app=WebAppInfo(url="https://yene-delivery.netlify.app/"),
            )
        ),
    )


async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    msg = (
        "Use /shipping to get an invoice for shipping-payment, or /no shipping for an "
        "invoice without shipping."
    )

    await update.message.reply_text(msg)

async def start_with_shipping_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    """Sends an invoice with shipping-payment."""    # new add

    await update.message.reply_text(
        "Welcome to Yene Delivery! Click the menu button to open the web app.",
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                text="Open Web App",
                web_app=WebAppInfo(url="https://yene-delivery.netlify.app/"),
            )
        ),
    )


async def start_without_shipping_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Sends an invoice without shipping-payment."""
    chat_id = update.message.chat_id
    title = "Burger"
    description = "Burger using python-telegram-bot"
    payload = "Custom-Payload"
    currency = "USD"

    # Add multiple products to the checkout list
    prices = [
        LabeledPrice("በርገር", 245),
        LabeledPrice("ፒዛ Special", 400),
        LabeledPrice("ላዛኛ", 653),
    ]

    await context.bot.send_invoice(
        chat_id, title, description, payload, PAYMENT_PROVIDER_TOKEN, currency, prices
    )

async def shipping_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Answers the ShippingQuery with ShippingOptions"""
    query = update.shipping_query
    if query.invoice_payload != "Custom-Payload":
        await query.answer(ok=False, error_message="Something went wrong...")
        return

    options = [ShippingOption("1", "Shipping Option A", [LabeledPrice("A", 100)])]
    price_list = [LabeledPrice("B1", 150), LabeledPrice("B2", 200)]
    options.append(ShippingOption("2", "Shipping Option B", price_list))
    await query.answer(ok=True, shipping_options=options)
async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Answers the PreCheckoutQuery"""
    query = update.pre_checkout_query
    if query.invoice_payload != "Custom-Payload":
        await query.answer(ok=False, error_message="Something went wrong...")
    else:
        await query.answer(ok=True)
async def web_app_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.web_app.url
    user_id = update.effective_user.id

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            # Process the response data as needed

        await context.bot.send_message(
            chat_id=user_id,
            text=f"Received data from the web app: {response.text}",
        )

    except httpx.HTTPError as e:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"An error occurred while retrieving data from the web app: {e}",
        )

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Confirms the successful payment."""
    await update.message.reply_text("Thank you for your payment!")

async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Print the received data and remove the button."""
    # Here we use `json.loads`, since the WebApp sends the data JSON serialized string
    # (see webappbot.html)
    data = json.loads(update.effective_message.web_app_data.data)

    chat_id = update.message.chat_id
    title_head = "Your Order Lists"
    description = "from AAA CAFE"
    payload = "Custom-Payload"
    currency = "USD"

    # Add multiple products to the checkout list
    prices = []
    for item in data:
        title = item['name']
        price = int(item['price']*100)
        # image=data[0]['image']
        # image=item['Image']
        prices.append(LabeledPrice(title, price))
    # add new feature
    # print('https://yene-delivery.netlify.app', data[0]['Image'])
    img_url=data[0]['image']
    base_url='https://yene-delivery.netlify.app'
    url_img=base_url+img_url
    print(url_img)
    await context.bot.send_invoice(
        chat_id,
        title_head,
        description,
        payload,
        PAYMENT_PROVIDER_TOKEN,
        currency,
        prices,
        need_name=True,
        need_phone_number=True,
        need_email=True,
        need_shipping_address=True,
        is_flexible=True,
        photo_url=str(img_url)
    )

    url = f"https://api.telegram.org/bot{token_send}/sendMessage"
    markup = {
        'inline_keyboard': [
            [
                {'text': 'Accept', 'callback_data': 'accept'},
                {'text': 'Decline', 'callback_data': 'decline'}
            ]
        ]
    }
    message = "Invoice Details:\n"
    message += " name    price      quantity\n"

    for labeled_price in prices:
        product_name = labeled_price.label
        price = str(labeled_price.amount)
        quantity = "1"

        formatted_row = "{:<15} {:<10} {:<10}\n".format(product_name, price, quantity)
        message += formatted_row

    payload = {
        'chat_id': "761513957",
        'text': f"New Order:\n\nName: {title_head}\nDescription: {description}\nCurrency: {currency}\nPrices:\n{message}\nNeed Name: True\nNeed Phone Number: True",
        'reply_markup': markup
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print("Invoice message sent successfully to the other Telegram bot.")
    else:
        print("Failed to send the invoice message.")



def main() -> None:
    """Run the bot."""
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start_with_shipping_callback))
    application.add_handler(CommandHandler("shipping", start_with_shipping_callback))
    application.add_handler(CommandHandler("noshipping", start_without_shipping_callback))
    application.add_handler(ShippingQueryHandler(shipping_callback))
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(
        MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback)
    )
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))

    # Add the bot.on('WebApp') event handler
    application.add_error_handler('WebApp', web_app_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, Updater
from PIL import Image



logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# FUNCTIONS

async def handle_received_image(update: Update, context: ContextTypes.DEFAULT_TYPE):

    image_file = context.bot.get_file(update.message.photo[-1].file_id)
    image_path = os.path.join("images", f"{image_file.file_id}.jpg")
    image_file.download(image_path)
    img = Image.open(image_path)

    png_path = os.path.join("images", f"{image_file.file_id}.png")
    img.save(png_path, "PNG")

    img = Image.open(png_path)
    if img.width > 512 or img.height > 512:
        img.thumbnail((512, 512))
        resized_image_path = os.path.join("images", f"{image_file.file_id}_resized.png")
        img.save(resized_image_path, "PNG")
    else:
        resized_image_path = png_path
    
    context.bot.upload_sticker_file(user_id=context.bot.get_me().id, sticker=context.bot.get_file(resized_image_path), sticker_format="PNG")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Finemang va?! Din sticker är nu tillagd!")


    

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Nå morjens påddi PhuxK '23 medlem! Vill du duuna lite stickers?\n \nSkicka din sticker till mig. Stickers måste rymmas in i en 512x512 kvadrat, så om din bild inte gör det sker en automatisk resizing. Ingen cropping sker, men i praktiken kan stickern bli lite mindre för att rymmas.")





# INITIALIZER
if __name__ == '__main__':
    application = ApplicationBuilder().token('6650602324:AAFXEkn6e1qGxhSB3dWM9q41x24-hEbMUu8').build()

    existing_pack = application.bot.get_sticker_set("PhuxK23")
    if not existing_pack:
        application.bot.createNewStickerSet(user_id=application.bot.get_me().id, name="PhuxK23", title="PhuxK '23 Sticker Päck", stickers=[], sticker_format="static")
        print("Created new sticker pack")
    else:
        print("Found existing sticker pack")
    
    start_handler = CommandHandler('start', start)
    image_handler = MessageHandler(filters.Filters.photo, handle_received_image)

    application.add_handler(start_handler)
    application.add_handler(image_handler)
    
    application.run_polling()
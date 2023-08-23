import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from PIL import Image
import os
import requests
from decouple import config, Csv




logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logging.getLogger('httpx').setLevel(logging.WARNING)


BOT_TOKEN = config('BOT_TOKEN')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["started"] = True
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Morjens PhuxK '23 medlem! Vill du duuna lite stickers?\n\nSkicka din sticker till mig. Stickers måste rymmas in i en 512x512 kvadrat, så om din bild inte gör det sker en automatisk resizing. Ingen cropping sker, men i praktiken kan stickern bli lite mindre för att rymmas.")


async def process_user_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
     if not context.user_data.get("started", False):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Nej, inte så. Skriv /start för att starta (duh)."
        )
        return 
     else:

        # Retrieve image
        file_id = None
        if update.message.document:
            file_id = update.message.document.file_id
        else:
            file_id = update.message.photo[-1].file_id
        image_file = await context.bot.get_file(file_id)
        image_path = os.path.join("images", f"{file_id}.png")

        # Download the file:
        await image_file.download_to_drive(image_path)
    
        # Convert to png
        image = Image.open(image_path)
        image.save(image_path, "PNG")

        # Resize if needed
        if image.width > 512 or image.height > 512:
            image.thumbnail((512, 512), Image.BICUBIC)
        
        # Prompt user for name and emoji

        # Create and add sticker to pack
        sticker = await context.bot.upload_sticker_file(user_id = (await context.bot.get_me()).id, sticker = open(image_path, 'rb'), sticker_format = "static")
    
        context.bot.add_sticker_to_set((await context.bot.get_me()).id, "PhuxK", sticker.file_id, "🥶")        

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Din shticker är nu fertig."
        )
         


async def wrong_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Nej, inte så. Skriv /start för att starta (duh).")



if __name__ == '__main__':
    application = ApplicationBuilder().token('BOT_TOKEN').build()
    
    start_handler = CommandHandler('start', start)
    wrong_command_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), wrong_command)
    process_user_image_handler = MessageHandler((filters.Document.IMAGE | filters.PHOTO) & (~filters.COMMAND), process_user_image)


    application.add_handler(start_handler)
    application.add_handler(wrong_command_handler)
    application.add_handler(process_user_image_handler)

    existing_pack = application.bot.get_sticker_set("PhuxK")
    if not existing_pack:
        
        application.bot.createNewStickerSet(
            user_id=application.bot.get_me().id,
            name="PhuxK",
            title="PhuxK '23 Sticker Päck",
            stickers=[],
            sticker_format="static"
        )
        print("Created new sticker pack.")

    else:
        print("Found existing sticker pack.") 



    application.run_polling()
from telegram.ext import Updater, CommandHandler, MessageHandler


# Función para enviar un mensaje a telegram
def broadcast_message(updater, mensaje):
    updater.bot.send_message(chat_id='@BuscacursosChecker', text=mensaje)


# Inicializa el bot:
def main():
    updater = Updater(token='828466731:AAGhMQ_C7MYULh1TgWKL6Q9WF_nrO7rN51c', use_context=True)
    dispatcher = updater.dispatcher
    updater.start_polling()
    return updater


if __name__ == '__main__':
    main()

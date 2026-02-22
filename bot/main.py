import os
import asyncio
import logging
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
TOKEN = os.environ.get('TELEGRAM_TOKEN', '')

WALLETS = {
    'BTC': 'bc1q...',
    'USDT_TRC20': 'T...',
    'ETH': '0x...'
}


def tpl_que_es_wlfi():
    return (
        "MODULO FAQ - QUE ES WLFI?\n"
        "World Liberty Financial es un proyecto DeFi de la familia Trump. Captura el 75% de los ingresos.\n"
        "Opera en https://www.binance.com"
    )


def tpl_ganancias_trump():
    return (
        "MODULO FAQ - GANANCIAS\n"
        "Se han vendido ~800M en tokens. La riqueza es volatil.\n"
        "Prueba https://www.kraken.com"
    )


def tpl_riesgos_ciudadano():
    return (
        "MODULO FAQ - ES SEGURO?\n"
        "Riesgo extremadamente alto. No inviertas lo que no puedas perder.\n"
        "Usa https://www.bybit.com"
    )


def tpl_plan_triplicado(nivel):
    if nivel == 'menu':
        return "EL PLAN TRIPLICADO: DE LA PERDIDA AL PODER\nElige un nivel para activar tu reconstruccion:"
    elif nivel == 'interior':
        return "NIVEL 1: TU PODER INTERIOR\n1. Escribe y quema tu rabia.\n2. Confiesa tu verguenza.\n3. Haz algo pequeho que dependa solo de ti."
    elif nivel == 'financiero':
        return "NIVEL 2: TU PODER FINANCIERO\n1. Ahorro Hormiga.\n2. Habilidad Oculta.\n3. Conocimiento Blindado."
    elif nivel == 'colectivo':
        return "NIVEL 3: TU PODER COLECTIVO\n1. Grupo de Apoyo.\n2. Comparte tu historia.\n3. Alianza Invisible."
    elif nivel == 'mantra':
        return "MANTRA: No cai para siempre, cai para aprender."
    return ""


def get_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("EL PLAN TRIPLICADO", callback_data='tri_menu')],
        [InlineKeyboardButton("Que es WLFI?", callback_data='que_es_wlfi')],
        [InlineKeyboardButton("Ganancias", callback_data='ganancias'),
         InlineKeyboardButton("Riesgos", callback_data='riesgos')],
        [InlineKeyboardButton("Donar", callback_data='donar')],
        [InlineKeyboardButton("Cerrar", callback_data='back')],
    ])


def get_tri_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Nivel 1 Interior", callback_data='tri_interior')],
        [InlineKeyboardButton("Nivel 2 Financiero", callback_data='tri_financiero')],
        [InlineKeyboardButton("Nivel 3 Colectivo", callback_data='tri_colectivo')],
        [InlineKeyboardButton("Mantra", callback_data='tri_mantra')],
        [InlineKeyboardButton("Volver al Menu", callback_data='back')],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = get_main_keyboard()
    text = "UNIVERSO WLF TRIPLICADO\nConvertimos tu perdida en poder absoluto. Elige:"
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    back = InlineKeyboardMarkup([[InlineKeyboardButton("Volver", callback_data='back')]])
    if data == 'que_es_wlfi':
        await query.edit_message_text(tpl_que_es_wlfi(), reply_markup=back)
    elif data == 'ganancias':
        await query.edit_message_text(tpl_ganancias_trump(), reply_markup=back)
    elif data == 'riesgos':
        await query.edit_message_text(tpl_riesgos_ciudadano(), reply_markup=back)
    elif data == 'tri_menu':
        await query.edit_message_text(tpl_plan_triplicado('menu'), reply_markup=get_tri_keyboard())
    elif data.startswith('tri_'):
        nivel = data.split('_', 1)[1]
        await query.edit_message_text(tpl_plan_triplicado(nivel), reply_markup=back)
    elif data == 'donar':
        text = "DONACIONES\nBTC: " + WALLETS['BTC'] + "\nUSDT: " + WALLETS['USDT_TRC20'] + "\nETH: " + WALLETS['ETH']
        await query.edit_message_text(text, reply_markup=back)
    elif data == 'back':
        await start(update, context)


async def process_update(token, data):
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))
    async with application:
        update = Update.de_json(data, application.bot)
        await application.process_update(update)


@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        asyncio.run(process_update(TOKEN, request.get_json(force=True)))
    except Exception as e:
        logger.error(f'Error: {e}')
    return jsonify({'ok': True})


@app.route('/')
def index():
    return jsonify({'status': 'running', 'bot': 'Barbosa WLF Triplicado'})


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

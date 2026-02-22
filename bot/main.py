import os
import asyncio
import logging
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, PreCheckoutQueryHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
TOKEN = os.environ.get('TELEGRAM_TOKEN', '')

WALLETS = {
    'BTC': 'bc1q...', # Placeholder
    'USDT_TRC20': 'T...', # Placeholder
    'ETH': '0x...' # Placeholder
}

def tpl_que_es_wlfi():
    return (
        "📌 MODULO FAQ - QUE ES WLFI?

"
        "Un proyecto DeFi de la familia Trump. Captura el 75% de ingresos.

"
        "👉 Opera en [Binance](https://www.binance.com)."
    )

def tpl_ganancias_trump():
    return (
        "💰 MODULO FAQ - GANANCIAS

"
        "~800M en tokens vendidos. Riqueza volatil.

"
        "👉 Prueba [Kraken](https://www.kraken.com)."
    )

def tpl_riesgos_ciudadano():
    return (
        "⚠️ MODULO FAQ - ES SEGURO?

"
        "Riesgo alto (88% perdida). No inviertas lo que no puedas perder.

"
        "👉 Usa [Bybit](https://www.bybit.com)."
    )

def tpl_simulador_perdidas(monto, premium=False):
    if not premium:
        return (
            f"🧮 SIMULADOR BASICO - INVERTIR {monto:.2f} USD

"
            f"Escenario 1 (68% probable): Pierdes -85% -> ~{monto*0.15:.2f} USD

"
            "🌟 ¡DESBLOQUEA EL PREMIUM PARA VER TODO! 🌟"
        )
    return (
        f"🚀 SIMULADOR PREMIUM - INVERTIR {monto:.2f} USD

"
        f"E1: -85% -> ~{monto*0.15:.2f}
"
        f"E2: -60% -> ~{monto*0.40:.2f}
"
        f"E3: 0% -> ~{monto:.2f}
"
        f"E4: +400% -> ~{monto*5:.2f}

"
        "💎 ANALISIS: Riesgo extremo. Moralbeja: Es loteria."
    )

def tpl_plan_triplicado(nivel):
    if nivel == 'menu':
        return (
            "🚀 **EL PLAN TRIPLICADO: DE LA PERDIDA AL PODER** 🚀

"
            "Elige un nivel para activar tu reconstruccion:"
        )
    elif nivel == 'interior':
        return (
            "🔥 **NIVEL 1: TU PODER INTERIOR (Sanacion)** 🔥

"
            "1. Escribe y quema tu rabia.
"
            "2. Confiesa tu vergüenza.
"
            "3. Haz algo pequeño que dependa solo de ti."
        )
    elif nivel == 'financiero':
        return (
            "💰 **NIVEL 2: TU PODER FINANCIERO (Reconstruccion)** 💰

"
            "1. Ahorro Hormiga ($1/dia).
"
            "2. Habilidad Oculta (Vende lo que sabes).
"
            "3. Conocimiento Blindado (Aprende finanzas)."
        )
    elif nivel == 'colectivo':
        return (
            "🌍 **NIVEL 3: TU PODER COLECTIVO (Comunidad)** 🌍

"
            "1. Grupo de Apoyo 'Los que ya no caemos'.
"
            "2. Comparte tu historia. Ayuda a otros.
"
            "3. Alianza Invisible con gente despierta."
        )
    elif nivel == 'mantra':
        return "🎯 **MANTRA:** _\"No cai para siempre, cai para aprender. Y lo que aprendi, nadie me lo quita.\"_"
    return ""

def get_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 EL PLAN TRIPLICADO", callback_data='tri_menu')],
        [InlineKeyboardButton("Que es WLFI?", callback_data='que_es_wlfi')],
        [InlineKeyboardButton("Ganancias", callback_data='ganancias'), InlineKeyboardButton("Riesgos", callback_data='riesgos')],
        [InlineKeyboardButton("Simulador Perdidas", callback_data='sim_info')],
        [InlineKeyboardButton("⭐ Desbloquear Premium", callback_data='buy_premium')],
        [InlineKeyboardButton("Debate Senado IA", callback_data='senado_menu')],
        [InlineKeyboardButton("Version Niños", callback_data='infantil'), InlineKeyboardButton("Propuesta Ley", callback_data='ley')],
        [InlineKeyboardButton("🙏 Donar", callback_data='donar'), InlineKeyboardButton("Manifiesto", callback_data='manifiesto')],
        [InlineKeyboardButton("Cerrar", callback_data='back')],
    ])

def get_tri_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 Nivel 1", callback_data='tri_interior')],
        [InlineKeyboardButton("💰 Nivel 2", callback_data='tri_financiero')],
        [InlineKeyboardButton("🌍 Nivel 3", callback_data='tri_colectivo')],
        [InlineKeyboardButton("🎯 Mantra", callback_data='tri_mantra')],
        [InlineKeyboardButton("Volver al Menu", callback_data='back')],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = get_main_keyboard()
    text = "🌟 **UNIVERSO WLF TRIPLICADO** 🌟

Convertimos tu perdida en poder absoluto. Elige:"
    if update.message: await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    else: await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer(); data = query.data
    back = InlineKeyboardMarkup([[InlineKeyboardButton("Volver", callback_data='back')]])
    if data == 'que_es_wlfi': await query.edit_message_text(tpl_que_es_wlfi(), reply_markup=back, parse_mode='Markdown')
    elif data == 'ganancias': await query.edit_message_text(tpl_ganancias_trump(), reply_markup=back, parse_mode='Markdown')
    elif data == 'riesgos': await query.edit_message_text(tpl_riesgos_ciudadano(), reply_markup=back, parse_mode='Markdown')
    elif data == 'tri_menu': await query.edit_message_text(tpl_plan_triplicado('menu'), reply_markup=get_tri_keyboard(), parse_mode='Markdown')
    elif data.startswith('tri_'): await query.edit_message_text(tpl_plan_triplicado(data.split('_')[1]), reply_markup=back, parse_mode='Markdown')
    elif data == 'back': await start(update, context)

async def process_update(token, data):
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))
    async with application:
        update = Update.de_json(data, application.bot)
        await application.process_update(update)

@app.route('/webhook', methods=['POST'])
def webhook():
    try: asyncio.run(process_update(TOKEN, request.get_json(force=True)))
    except Exception as e: logger.error(f'Error: {e}')
    return jsonify({'ok': True})

@app.route('/')
def index(): return jsonify({'status': 'running', 'bot': 'Barbosa WLF Triplicado'})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

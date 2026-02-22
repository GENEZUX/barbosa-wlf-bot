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

# ====== WALLETS DONACIONES ======
WALLETS = {
    'BTC': 'bc1q...', # Placeholder
    'USDT_TRC20': 'T...', # Placeholder
    'ETH': '0x...' # Placeholder
}

# ====== EL UNIVERSO WLF - MODULOS ACTUALIZADOS ======

def tpl_que_es_wlfi():
    return (
        "📌 MODULO FAQ - QUE ES WLFI?

"
        "Un proyecto de criptomonedas de la familia Trump donde crean su propio token WLFI y su moneda USD1.
"
        "Es un protocolo DeFi (finanzas descentralizadas) que ofrece prestamos y credito.

"
        "Captura de valor: La familia recibe el 75% de los ingresos netos por venta de tokens.

"
        "👉 Registrate en [Binance](https://www.binance.com) para operar con seguridad."
    )

def tpl_ganancias_trump():
    return (
        "💰 MODULO FAQ - GANANCIAS

"
        "Efectivo real: ~800 millones por venta de tokens (Reuters).
"
        "Riqueza en papel: Entre 5,000 y 7,500 millones en tokens sin vender.

"
        "Esta riqueza es volatil y depende de que el precio se mantenga.

"
        "👉 Empieza a invertir con mi link de [Kraken](https://www.kraken.com)."
    )

def tpl_riesgos_ciudadano():
    return (
        "⚠️ MODULO FAQ - ES SEGURO?

"
        "No. Riesgo alto. Probabilidad del 88% de perder dinero segun modelos.
"
        "Historico: Trump Coin -94%, Melania Coin -90%.

"
        "Hacienda IA recomienda: No inviertas lo que no puedas perder.

"
        "👉 Protege tus activos en un exchange seguro como [Bybit](https://www.bybit.com)."
    )

def tpl_simulador_perdidas(monto, premium=False):
    if not premium:
        return (
            f"🧮 SIMULADOR BASICO - INVERTIR {monto:.2f} USD

"
            f"Escenario 1 (68% probable): Pierdes -85% -> Valor final ~{monto*0.15:.2f} USD
"
            "VALOR ESPERADO: Pierdes gran parte de tu inversion.

"
            "🌟 ¡DESBLOQUEA EL SIMULADOR PREMIUM! 🌟
"
            "Obten los 4 escenarios detallados, calculo de riesgo especifico y consejos de Hacienda IA por solo 10 Estrellas."
        )
    else:
        return (
            f"🚀 SIMULADOR PREMIUM ACTIVADO - INVERTIR {monto:.2f} USD

"
            f"Escenario 1 (68% probable): Pierdes -85% -> Valor final ~{monto*0.15:.2f} USD
"
            f"Escenario 2 (20% probable): Pierdes -60% -> Valor final ~{monto*0.40:.2f} USD
"
            f"Escenario 3 (10% probable): Recuperas 0% -> Valor final ~{monto:.2f} USD
"
            f"Escenario 4 (2% probable): Ganas +400% -> Valor final ~{monto*5:.2f} USD

"
            "💎 ANALISIS DE HACIENDA IA:
"
            "- Factor de riesgo: 9.2/10
"
            "- Recomendacion: Diversificar fuera del ecosistema WLF.
"
            "- Moralbeja: Es una loteria, no una inversion segura."
        )

def tpl_donar():
    return (
        "🙏 ¡GRACIAS POR TU APOYO! 🙏

"
        "Tus donaciones ayudan a mantener el bot libre de publicidad y actualizado.

"
        f"📍 BTC (Native SegWit): `{WALLETS['BTC']}`
"
        f"📍 USDT (TRC-20): `{WALLETS['USDT_TRC20']}`
"
        f"📍 ETH / Polygon: `{WALLETS['ETH']}`

"
        "Copia la direccion tocando sobre ella."
    )

def tpl_senado_ia(rol):
    if rol == 'innovacion':
        return (
            "🎭 SENADOR A - PARTIDO INNOVACION PRO WLF

"
            "Es el Apple del futuro financiero! Estamos uniendo cripto con el dolar.
"
            "Es patriotismo financiero. El que innova y se arriesga, cosecha. Se valiente!"
        )
    elif rol == 'transparencia':
        return (
            "🎭 SENADOR B - PARTIDO TRANSPARENCIA CONTRA WLF

"
            "El 75% para ellos, el riesgo para ti. Es una empresa familiar disfrazada de blockchain.
"
            "Estan vendiendo sueños de papel pintado. No seas el tonto final."
        )
    elif rol == 'pueblo':
        return (
            "🎭 SENADORA C - PARTIDO DEL PUEBLO

"
            "No seas el tonto de la fiesta, mi vida! Si no lo entiendes, no lo compres.
"
            "Ellos juegan monopoly, tu juegas con tu futuro. Cuida tu bolsillo!"
        )
    elif rol == 'datos':
        return (
            "🎭 SENADOR E - PARTIDO CIENTIFICO-DATOS

"
            "Factor de riesgo de centralizacion: 8.7/10. Probabilidad 88% de perder dinero.
"
            "Los datos no mienten, las personas si. Valor esperado negativo."
        )
    return "Elige un Senador para el debate."

def tpl_version_infantil():
    return (
        "🧒 HACIENDA IA PARA NIÑOS

"
        "Habia una vez una familia famosa que invento su moneda de Monopoly real.
"
        "Le dijeron a todos: 'Danos tus dulces y te damos nuestra moneda magica'.
"
        "La gente dio sus dulces, la familia se hizo rica, pero la moneda magica no compraba helados.

"
        "Leccion: Si no sirve para nada, cuidado!"
    )

def tpl_ley_wlf():
    return (
        "⚖️ PROYECTO DE LEY N 001-2026-GIA

"
        "TITULO I: Transparencia obligatoria de carteras publicas.
"
        "TITULO II: Limite de fundadores al 20% del suministro.
"
        "TITULO III: Separacion de poderes (Fideicomiso ciego).
"
        "TITULO IV: Proteccion al inversor (7 dias para arrepentirse)."
    )

def tpl_manifiesto():
    return (
        "📜 MANIFIESTO DEL PUEBLO

"
        "Basta de vendernos humo! Basta de usar el poder para crear dinero!
"
        "Queremos un mundo donde el trabajo valga por lo que produce.
"
        "La mejor inversion es una comunidad que se quiere."
    )

def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("Que es WLFI?", callback_data='que_es_wlfi')],
        [InlineKeyboardButton("Ganancias", callback_data='ganancias'), InlineKeyboardButton("Riesgos/Seguridad", callback_data='riesgos')],
        [InlineKeyboardButton("Simulador Perdidas", callback_data='sim_info')],
        [InlineKeyboardButton("⭐ Desbloquear Premium", callback_data='buy_premium')],
        [InlineKeyboardButton("Debate Senado IA", callback_data='senado_menu')],
        [InlineKeyboardButton("Version Niños", callback_data='infantil'), InlineKeyboardButton("Propuesta Ley", callback_data='ley')],
        [InlineKeyboardButton("🙏 Donar", callback_data='donar'), InlineKeyboardButton("Manifiesto", callback_data='manifiesto')],
        [InlineKeyboardButton("Cerrar", callback_data='back')],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_senado_keyboard():
    keyboard = [
        [InlineKeyboardButton("Senador A (Pro)", callback_data='senado_innovacion')],
        [InlineKeyboardButton("Senador B (Contra)", callback_data='senado_transparencia')],
        [InlineKeyboardButton("Senadora C (Pueblo)", callback_data='senado_pueblo')],
        [InlineKeyboardButton("Senador E (Datos)", callback_data='senado_datos')],
        [InlineKeyboardButton("Volver al Menu", callback_data='back')],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = get_main_keyboard()
    welcome_text = (
        "🌟 BIENVENIDO AL UNIVERSO WLF MONETIZADO 🌟

"
        "Aqui tienes todo: desde debates de Senadores IA hasta simuladores premium.
"
        "Elige un area para activar el conocimiento:"
    )
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.callback_query.edit_message_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def buy_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat_id
    title = "Acceso Premium - Simulador WLF"
    description = "Desbloquea todos los escenarios del simulador y analisis detallado de Hacienda IA."
    payload = "premium_payload"
    currency = "XTR"  # Telegram Stars
    price = 10
    prices = [LabeledPrice("Premium", price)]

    await context.bot.send_invoice(
        chat_id, title, description, payload, "", currency, prices
    )

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    if query.invoice_payload != "premium_payload":
        await query.answer(ok=False, error_message="Algo salio mal...")
    else:
        await query.answer(ok=True)

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ ¡Pago exitoso! Ahora tienes acceso al Simulador Premium. Usa: sim 1000")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Volver al Menu", callback_data='back')]])
    
    if data == 'que_es_wlfi':
        await query.edit_message_text(text=tpl_que_es_wlfi(), reply_markup=back_markup, parse_mode='Markdown')
    elif data == 'ganancias':
        await query.edit_message_text(text=tpl_ganancias_trump(), reply_markup=back_markup, parse_mode='Markdown')
    elif data == 'riesgos':
        await query.edit_message_text(text=tpl_riesgos_ciudadano(), reply_markup=back_markup, parse_mode='Markdown')
    elif data == 'sim_info':
        await query.edit_message_text(text="Escribe directamente: sim 1000 para calcular. El modo premium desbloquea el analisis completo.", reply_markup=back_markup)
    elif data == 'buy_premium':
        await buy_premium(update, context)
    elif data == 'donar':
        await query.edit_message_text(text=tpl_donar(), reply_markup=back_markup, parse_mode='Markdown')
    elif data == 'senado_menu':
        await query.edit_message_text(text="🎭 ELIGE UN SENADOR PARA ESCUCHAR SU POSTURA:", reply_markup=get_senado_keyboard())
    elif data.startswith('senado_'):
        rol = data.split('_')[1]
        await query.edit_message_text(text=tpl_senado_ia(rol), reply_markup=back_markup)
    elif data == 'infantil':
        await query.edit_message_text(text=tpl_version_infantil(), reply_markup=back_markup)
    elif data == 'ley':
        await query.edit_message_text(text=tpl_ley_wlf(), reply_markup=back_markup)
    elif data == 'manifiesto':
        await query.edit_message_text(text=tpl_manifiesto(), reply_markup=back_markup)
    elif data == 'back':
        await start(update, context)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower().strip()
    if text.startswith('sim'):
        parts = text.split()
        if len(parts) >= 2:
            try:
                monto = float(parts[1])
                # Nota: En un sistema real, verificariamos si el usuario ha pagado el premium en una DB.
                # Aqui simulamos la diferencia.
                await update.message.reply_text(tpl_simulador_perdidas(monto, premium=False))
            except ValueError:
                await update.message.reply_text("Formato: sim 1000")
    else:
        await update.message.reply_text("Usa /start para ver el menu.")

async def process_update(token, data):
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    async with application:
        update = Update.de_json(data, application.bot)
        await application.process_update(update)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True)
        asyncio.run(process_update(TOKEN, data))
    except Exception as e:
        logger.error(f'Webhook error: {e}')
    return jsonify({'ok': True})

@app.route('/')
def index():
    return jsonify({'status': 'running', 'bot': 'Barbosa WLF - Monetizado'})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

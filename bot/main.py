import os
import asyncio
import logging
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
TOKEN = os.environ.get('TELEGRAM_TOKEN', '')

# ====== MODULO HACIENDAIA_WLFI ======

def tpl_que_es_wlfi():
    return (
        "HACIENDA IA - QUE ES WORLD LIBERTY FINANCIAL (WLFI)?\n\n"
        "World Liberty Financial es un protocolo DeFi ligado a la familia Trump.\n"
        "Tiene dos piezas: el token de gobernanza WLFI y la stablecoin USD1 pegada al dolar.\n\n"
        "WLFI sirve para votar en el protocolo, pagar comisiones y acceder a productos DeFi.\n"
        "USD1 es la moneda estable para pagos y prestamos dentro de la plataforma.\n\n"
        "En palabras simples: un sistema financiero digital donde una familia politica poderosa\n"
        "tiene rol central tanto en el negocio como en el diseno de las reglas."
    )

def tpl_estructura_wlfi():
    return (
        "ESTRUCTURA BASICA DE WLFI\n\n"
        "1) Token WLFI (gobernanza):\n"
        "   - Da derecho a votar en decisiones del protocolo.\n"
        "   - Se usa para comisiones y productos avanzados.\n\n"
        "2) Stablecoin USD1:\n"
        "   - Paridad 1 USD1 = 1 dolar (en teoria).\n"
        "   - Moneda estable para pagos y prestamos.\n\n"
        "3) Protocolo DeFi:\n"
        "   - Prestamos, trading y colateral cripto (ETH, BTC, USDC, USDT).\n\n"
        "4) Captura de valor:\n"
        "   - Una entidad ligada a la familia recibe la mayor parte de los ingresos."
    )

def tpl_ganancias_trump():
    return (
        "GANANCIAS DE LA FAMILIA TRUMP CON WLFI\n\n"
        "Una entidad vinculada a la familia controla una gran parte de los tokens WLFI\n"
        "y recibe la mayoria de los ingresos del proyecto.\n\n"
        "El valor teorico de su participacion ha alcanzado miles de millones en papel,\n"
        "mas cientos de millones en ingresos efectivos por ventas y comisiones.\n\n"
        "Traduccion Barbosa: el diseno economico esta hecho para que ellos capturen\n"
        "la porcion mas grande del pastel."
    )

def tpl_riesgos_ciudadano():
    return (
        "RIESGOS PARA EL CIUDADANO\n\n"
        "1) Volatilidad extrema: el precio puede subir o caer muy rapido.\n"
        "2) Asimetria de informacion: insiders tienen mejor timing que el ciudadano comun.\n"
        "3) Riqueza en papel: gran parte del valor puede desaparecer si cambia el mercado.\n"
        "4) Historial: otros tokens politicos han caido mas del 90% desde sus maximos.\n\n"
        "Conclusion: no es ahorro garantizado, es apuesta especulativa."
    )

def tpl_predicciones_wlfi():
    return (
        "PREDICCIONES WLFI 2027-2030 (EDUCATIVO, NO CONSEJO FINANCIERO)\n\n"
        "Rangos ilustrativos segun distintos modelos:\n\n"
        "2027:\n"
        "  Conservador: ~0.18 USD\n"
        "  Moderado: ~0.50 USD\n"
        "  Agresivo: ~1.40 USD\n\n"
        "2030:\n"
        "  Muy conservador: ~0.15 USD\n"
        "  Moderado: ~0.30-0.50 USD\n"
        "  Ultra bull: ~2.00-5.00 USD\n\n"
        "Nada de esto es promesa. Son escenarios. WLFI sigue siendo un activo altamente especulativo."
    )

def tpl_comparativa_trump_tokens():
    return (
        "WLFI VS OTROS TOKENS TRUMP\n\n"
        "WLFI: token de gobernanza con uso dentro de protocolo DeFi + stablecoin propia.\n"
        "Memecoins TRUMP/MELANIA: fichas puramente especulativas, varias con caidas superiores al 90%.\n\n"
        "Leccion Barbosa: WLFI tiene mas estructura, pero el riesgo de\n"
        "perder dinero sigue siendo real para el ciudadano."
    )

def tpl_simulador_wlfi(monto):
    return (
        f"SIMULADOR EDUCATIVO - INVERTIR {monto:.2f} USD EN WLFI\n\n"
        "Rangos ilustrativos (no es prediccion exacta):\n\n"
        f"Escenario conservador (2027): ~{monto*0.18:.2f} USD (perdida fuerte)\n"
        f"Escenario medio (2027): ~{monto*0.50:.2f} USD (cerca del monto inicial)\n"
        f"Escenario agresivo (2027): ~{monto*1.40:.2f} USD (ganancia posible)\n\n"
        "MORALEJA BARBOSA: es mas parecido a una loteria financiera\n"
        "que a una cuenta de ahorro. Solo invierte lo que puedas perder."
    )

def tpl_conflicto_interes():
    return (
        "CONFLICTO DE INTERES\n\n"
        "World Liberty Financial esta ligado a una familia con poder politico y mediatico\n"
        "que tambien captura la mayor parte de las ganancias del proyecto.\n\n"
        "Pregunta central Barbosa:\n"
        "Es sano que quienes crean y poseen un activo financiero privado\n"
        "puedan tambien influir en las reglas que lo regulan?"
    )

def tpl_resumen_rapido():
    return (
        "RESUMEN RAPIDO WLFI - ESTILO BARBOSA\n\n"
        "Es un sistema cripto ligado a la familia Trump (token WLFI + moneda USD1).\n"
        "Ellos se quedan con la mayor parte de las ganancias.\n"
        "Tu asumes el riesgo fuerte de volatilidad y perdida de capital.\n"
        "Es un negocio privado con marca politica, no un banco publico."
    )

def tpl_debate_senado():
    return (
        "SENADO IA - MINI DEBATE WLFI\n\n"
        "Senador IA A (pro-WLFI):\n"
        "Es innovacion financiera patriotica que integra el dolar en el mundo cripto.\n\n"
        "Senador IA B (critico):\n"
        "Es un diseno donde una elite politica captura la mayoria de las ganancias\n"
        "y puede influir en las reglas que regulan su propio activo.\n\n"
        "Barbosa te pregunta:\n"
        "De que lado te colocarias si tu prioridad es proteger al ciudadano comun?"
    )

def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("Que es WLFI?", callback_data='que_es_wlfi')],
        [InlineKeyboardButton("Estructura", callback_data='estructura'), InlineKeyboardButton("Ganancias Trump", callback_data='ganancias')],
        [InlineKeyboardButton("Riesgos", callback_data='riesgos'), InlineKeyboardButton("Predicciones", callback_data='predicciones')],
        [InlineKeyboardButton("Comparar Tokens", callback_data='comparar')],
        [InlineKeyboardButton("Simulador (escribe: sim 1000)", callback_data='simulador_info')],
        [InlineKeyboardButton("Conflicto de Interes", callback_data='conflicto')],
        [InlineKeyboardButton("Resumen Rapido", callback_data='resumen'), InlineKeyboardButton("Senado IA", callback_data='senado')],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = get_main_keyboard()
    welcome_text = (
        "Bienvenido a Barbosa WLF - Tu Hacienda IA critica sobre World Liberty Financial.\n\n"
        "Aqui encontraras informacion educativa y critica sobre WLFI, USD1 y el ecosistema\n"
        "financiero de la familia Trump. Nada de esto es consejo financiero.\n\n"
        "Elige una opcion del menu:"
    )
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(welcome_text, reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    back_keyboard = [[InlineKeyboardButton("Volver al Menu", callback_data='back')]]
    back_markup = InlineKeyboardMarkup(back_keyboard)

    if data == 'que_es_wlfi':
        text = tpl_que_es_wlfi()
    elif data == 'estructura':
        text = tpl_estructura_wlfi()
    elif data == 'ganancias':
        text = tpl_ganancias_trump()
    elif data == 'riesgos':
        text = tpl_riesgos_ciudadano()
    elif data == 'predicciones':
        text = tpl_predicciones_wlfi()
    elif data == 'comparar':
        text = tpl_comparativa_trump_tokens()
    elif data == 'simulador_info':
        text = "Para usar el simulador, escribe directamente: sim 1000 (o el monto en USD que quieras analizar).\n\nEjemplo: sim 500"
    elif data == 'conflicto':
        text = tpl_conflicto_interes()
    elif data == 'resumen':
        text = tpl_resumen_rapido()
    elif data == 'senado':
        text = tpl_debate_senado()
    elif data == 'back':
        await start(update, context)
        return
    else:
        text = "Opcion no valida."

    await query.edit_message_text(text=text, reply_markup=back_markup)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower().strip()
    if text.startswith('sim'):
        parts = text.split()
        if len(parts) >= 2:
            try:
                monto = float(parts[1])
                await update.message.reply_text(tpl_simulador_wlfi(monto))
            except ValueError:
                await update.message.reply_text("Formato: sim 1000 (solo numeros)")
        else:
            await update.message.reply_text("Formato: sim 1000")
    else:
        await update.message.reply_text(
            "Usa /start para ver el menu de Barbosa WLF.\n"
            "O escribe: sim 1000 para el simulador educativo."
        )

async def process_update(token, data):
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))
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
    return jsonify({'status': 'running', 'bot': 'Barbosa WLF - Hacienda IA'})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

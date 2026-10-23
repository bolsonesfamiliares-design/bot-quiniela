from flask import Flask, request, jsonify
import random
import requests

app = Flask(__name__)

# --- CONFIGURACIÓN DE META WHATSAPP CLOUD API ---
VERIFY_TOKEN = "quiniela123"                  # El token secreto que pusiste en Meta
WHATSAPP_TOKEN = "TU_TOKEN_PERMANENTE_O_TEMPORAL_DE_META"   # Token de acceso de Meta Developers
PHONE_NUMBER_ID = "TU_PHONE_NUMBER_ID"    # ID del número de teléfono provisto por Meta

# Base de datos simulada de usuarios en memoria
usuarios_db = {}

def obtener_o_crear_usuario(telefono):
    """Inicializa la sesión de un cliente si no existe en memoria."""
    if telefono not in usuarios_db:
        usuarios_db[telefono] = {
            "paso_actual": "INICIO",
            "saldo": 5000,  # Saldo inicial de prueba
            "ticket_temporal": {}
        }
    return usuarios_db[telefono]

def procesar_mensaje_whatsapp(telefono, mensaje_recibido):
    """
    Función principal que procesa cada mensaje entrante 
    según el estado actual del usuario (paso_actual).
    """
    usuario = obtener_o_crear_usuario(telefono)
    paso = usuario["paso_actual"]
    mensaje = mensaje_recibido.strip()

    # PASO 1: MENÚ INICIAL DE BIENVENIDA
    if paso == "INICIO":
        usuario["paso_actual"] = "ESPERANDO_NUMERO"
        usuario["ticket_temporal"] = {}  
        
        return (
            "🎰 *¡Bienvenido a la Quiniela Nacional por WhatsApp!*\n\n"
            f"💰 Tu saldo disponible: *${usuario['saldo']}*\n\n"
            "Por favor, ingresa el *número* que deseas jugar\n"
            "_(De 1 a 4 cifras, ej: 8, 12, 542, 4812)_:"
        )

    # PASO 2: CAPTURA Y VALIDACIÓN DEL NÚMERO
    elif paso == "ESPERANDO_NUMERO":
        if mensaje.isdigit() and 1 <= len(mensaje) <= 4:
            numero_jugado = mensaje.zfill(len(mensaje))
            usuario["ticket_temporal"]["numero"] = numero_jugado
            usuario["paso_actual"] = "ESPERANDO_POSICION"

            return (
                f"✅ Número anotado: *{numero_jugado}*\n\n"
                "¿A qué ubicación querés apostar?\n"
                "1️⃣ A la Cabeza (1° lugar)\n"
                "2️⃣ A los 5\n"
                "3️⃣ A los 10\n"
                "4️⃣ A los 20\n\n"
                "_(Responde con el número de opción: 1, 2, 3 o 4)_"
            )
        else:
            return (
                "❌ *Número inválido.*\n"
                "Por favor, ingresa solo números de hasta 4 cifras (ej: 04, 812, 4812)."
            )

    # PASO 3: SELECCIÓN DE LA POSICIÓN
    elif paso == "ESPERANDO_POSICION":
        opciones_posicion = {
            "1": "A la Cabeza",
            "2": "A los 5",
            "3": "A los 10",
            "4": "A los 20"
        }

        if mensaje in opciones_posicion:
            posicion_elegida = opciones_posicion[mensaje]
            usuario["ticket_temporal"]["posicion"] = posicion_elegida
            usuario["paso_actual"] = "ESPERANDO_MONTO"

            return (
                f"📍 Posición guardada: *{posicion_elegida}*\n\n"
                "¿Cuánto dinero deseas apostar a este número?\n"
                "_(Ingresa el monto en pesos, ej: 100, 250, 500)_"
            )
        else:
            return (
                "❌ *Opción no válida.*\n"
                "Por favor responde con:\n"
                "1 (Cabeza), 2 (A los 5), 3 (A los 10) o 4 (A los 20)."
            )

    # PASO 4: VALIDACIÓN DE MONTO Y SALDO
    elif paso == "ESPERANDO_MONTO":
        if mensaje.isdigit() and int(mensaje) > 0:
            monto = int(mensaje)
            
            if monto <= usuario["saldo"]:
                usuario["ticket_temporal"]["monto"] = monto
                usuario["paso_actual"] = "CONFIRMACION"

                t = usuario["ticket_temporal"]
                return (
                    "📝 *RESUMEN DE TU JUGADA:*\n\n"
                    f"• Número: *{t['numero']}*\n"
                    f"• Posición: *{t['posicion']}*\n"
                    f"• Monto: *${t['monto']}*\n\n"
                    "¿Confirmas la apuesta?\n"
                    "1️⃣ *SÍ*, confirmar jugada\n"
                    "2️⃣ *NO*, cancelar"
                )
            else:
                return (
                    f"⚠️ *Saldo insuficiente.*\n"
                    f"Tu saldo actual es de *${usuario['saldo']}*.\n"
                    "Por favor, ingresa un monto menor o carga saldo."
                )
        else:
            return "❌ Por favor, ingresa un monto válido en números (ej: 200)."

    # PASO 5: EMISIÓN DEL TICKET
    elif paso == "CONFIRMACION":
        if mensaje == "1":
            monto = usuario["ticket_temporal"]["monto"]
            usuario["saldo"] -= monto
            id_ticket = f"TQ-{random.randint(10000, 99999)}"
            t = usuario["ticket_temporal"]
            
            usuario["paso_actual"] = "INICIO"

            return (
                "🎟️ *¡TICKET CONFIRMADO EXITOSAMENTE!*\n"
                "───────────────────────────────\n"
                f"ID Ticket: *#{id_ticket}*\n"
                f"Número: *{t['numero']}*\n"
                f"Ubicación: *{t['posicion']}*\n"
                f"Monto Apostado: *${t['monto']}*\n"
                f"Saldo Restante: *${usuario['saldo']}*\n"
                "───────────────────────────────\n"
                "¡Mucha suerte! Te avisaremos al finalizar el sorteo.\n\n"
                "_(Escribe 'Hola' cuando quieras hacer otra apuesta)_"
            )
        elif mensaje == "2":
            usuario["paso_actual"] = "INICIO"
            return "🚫 Jugada cancelada. Escribe cualquier mensaje para volver al inicio."
        else:
            return "Por favor responde *1* para confirmar o *2* para cancelar."

def enviar_respuesta_whatsapp(telefono, texto_respuesta):
    """Envía la respuesta de vuelta al usuario usando la Cloud API de Meta."""
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": telefono,
        "type": "text",
        "text": {"body": texto_respuesta}
    }
    requests.post(url, json=payload, headers=headers)

# ENDPOINT DE FLASK (WEBHOOK PARA META)
@app.route("/whatsapp", methods=["GET", "POST"])
def webhook_whatsapp():
    # 1. VERIFICACIÓN DEL WEBHOOK POR PARTE DE META (GET)
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode and token:
            if mode == "subscribe" and token == VERIFY_TOKEN:
                return challenge, 200
            else:
                return "Token de verificación incorrecto", 403
        return "Petición no válida", 400

    # 2. RECEPCIÓN DE MENSAJES DE WHATSAPP (POST)
    elif request.method == "POST":
        data = request.get_json()
        
        try:
            # Extraer los datos del mensaje entrante de Meta
            cambio = data["entry"][0]["changes"][0]["value"]
            if "messages" in cambio:
                mensaje_data = cambio["messages"][0]
                telefono = mensaje_data["from"]
                mensaje_recibido = mensaje_data["text"]["body"]

                # Procesar lógica del bot
                respuesta_bot = procesar_mensaje_whatsapp(telefono, mensaje_recibido)

                # Enviar mensaje de vuelta por WhatsApp
                enviar_respuesta_whatsapp(telefono, respuesta_bot)
        except (KeyError, IndexError):
            # Si es una notificación de estado (entregado, leído) se ignora sin romper el servidor
            pass

        return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)

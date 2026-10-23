import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configuración de credenciales de Meta y tu Bot
# Puedes cargarlas desde las variables de entorno de Render o dejarlas definidas aquí para pruebas rápidas.
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "EAAp4vgiBprkBS1NOL1KBFc8lXKgZBMnT6l4adVeEEZA2lPzZA0orgZB0xFEB4oooXuXEIQmJzjiSKNnIMxZCow30C8HDsihwZBmVXMY4rvQPVGgKUUZB5Xj6BkYMA6Ps9JDIk6v1NIFu622rVwNhzlxQqkZCI2j3OhnR0DrseUMo0bgFOeZCd7aPttpLnVLCsLhBfHQajFClr2BUAAwYWPlujW2YbOtpcE9RIKADKB9HyZC7SXUmXlZBoFIsvq3AStZCucYrhLzInnTO6EoxBt7v2mxbJK5D")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "1307957199078751")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "quiniela123")

@app.route("/", methods=["GET"])
def home():
    return "¡El bot de Quiniela en Línea está funcionando correctamente!", 200

# Ruta del Webhook configurada en Meta (/whatsapp)
@app.route("/whatsapp", methods=["GET", "POST"])
def webhook():
    # 1. Verificación del Webhook por parte de Meta (Petición GET)
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode and token:
            if mode == "subscribe" and token == VERIFY_TOKEN:
                print("WEBHOOK_VERIFIED: El Webhook se verificó correctamente con Meta.")
                return challenge, 200
            else:
                return "Token de verificación incorrecto", 403
        return "Parámetros inválidos", 400

    # 2. Recepción de mensajes de WhatsApp (Petición POST)
    elif request.method == "POST":
        data = request.json
        print("Mensaje recibido de Meta:", data)

        try:
            # Extraer información del mensaje entrante
            changes = data["entry"][0]["changes"][0]
            value = changes["value"]
            
            if "messages" in value:
                phone_number_id = value["metadata"]["phone_number_id"]
                from_number = value["messages"][0]["from"]
                msg_body = value["messages"][0]["text"]["body"].strip()

                print(f"Mensaje de {from_number}: {msg_body}")

                # Lógica de respuesta automática para la Quiniela
                responder_mensaje(phone_number_id, from_number, msg_body)

        except Exception as e:
            print(f"Error procesando el mensaje: {e}")

        return jsonify({"status": "success"}), 200

def responder_mensaje(phone_number_id, to_number, mensaje):
    """Función para enviar mensajes de respuesta a través de la API de Meta"""
    url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    # Texto de respuesta predeterminado para la Quiniela
    texto_respuesta = f"¡Hola! Recibí tu mensaje: '{mensaje}'. Bienvenido a Quiniela en Línea. Escribe 'apostar' o consulta tu jugada."

    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": texto_respuesta}
    }

    response = requests.post(url, json=payload, headers=headers)
    print("Respuesta enviada a Meta:", response.status_code, response.text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import requests

app = Flask(__name__)

# Configuración de base de datos (SQLite local / PostgreSQL en Render)
database_url = os.environ.get("DATABASE_URL")
if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiniela.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Apuesta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jugador = db.Column(db.String(100), nullable=False)
    numero = db.Column(db.String(2), nullable=False)
    monto = db.Column(db.Float, nullable=False)

with app.app_context():
    db.create_all()

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "mi_token_secreto_quiniela_123")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN", "EAAp4vgiBprkBS5YrgbPxJAmzLMZANnZCdl3vOk3nv7O8lDx9OZBs3Q1DwOgZCcQcW2P7YDYim0pcBwTlx6ynXNcPZCWGHgalPmQ6HZAPdrGh7SGRbKBy5LeOLBOnsBzKJNCqHro6KLAJbXa732V70Gfte123fOBBBZAiH4r2HmGnyp4SVyvYZA2L4Le6dbKtV5my8pFq79TYZA2uxoujD7eZC6qCjLJXaTK8lwuW7GykKfgdzmaos3HsJSTnQ5FFPW9tbbZCshFZBCegZBzZBddT2ZCloBx874K")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID", "1307957199078751")

def enviar_mensaje_whatsapp(destinatario, texto):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": destinatario,
        "type": "text",
        "text": {"body": texto}
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        print(f"Error enviando mensaje: {e}")
        return None

@app.route('/')
def index():
    apuestas = Apuesta.query.order_by(Apuesta.id.desc()).all()
    return f"<h1>Quiniela en línea</h1><p>Apuestas registradas: {len(apuestas)}</p>"

# Soporte dual para GET (Verificación de Meta)
@app.route('/webhook', methods=['GET'])
@app.route('/whatsapp', methods=['GET'])
def verificar_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        return challenge, 200
    return "Token incorrecto", 403

# Soporte dual para POST (Mensajes de WhatsApp)
@app.route('/webhook', methods=['POST'])
@app.route('/whatsapp', methods=['POST'])
def recibir_mensajes():
    data = request.get_json()
    try:
        if data and data.get('object'):
            for entry in data['entry']:
                for change in entry['changes']:
                    value = change.get('value', {})
                    if 'messages' in value:
                        mensaje_info = value['messages'][0]
                        numero_remitente = mensaje_info['from']
                        texto_mensaje = mensaje_info['text']['body'].strip()
                        
                        partes = [p.strip() for p in texto_mensaje.split(',')]
                        if len(partes) == 3:
                            jugador, numero_str, monto_str = partes
                            nueva = Apuesta(jugador=jugador, numero=numero_str.zfill(2), monto=float(monto_str))
                            db.session.add(nueva)
                            db.session.commit()
                            enviar_mensaje_whatsapp(numero_remitente, f"✅ Apuesta registrada: {jugador} - {numero_str} - ${monto_str}")
                        else:
                            enviar_mensaje_whatsapp(numero_remitente, "⚠️ Usa el formato: Nombre, Numero, Monto")
        return "EVENT_RECEIVED", 200
    except Exception as e:
        print(f"Error en webhook: {e}")
        return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
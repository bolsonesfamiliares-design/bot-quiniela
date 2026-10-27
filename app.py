import os
import re
import requests
from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# ==========================================
# CONFIGURACIÓN DE VARIABLES DE ENTORNO
# ==========================================
# Token de verificación para el Webhook (coincide con Meta)
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "mi_token_secreto_quiniela_123")

# Token de acceso actualizado de WhatsApp (Meta)
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN", "EAAp4vgiBprkBS3C01OKq4OQTbiBHT2oIpA2z7ZAM9tHwT2SlAuD7Wpk2iDhgZAFZAtAU6FUE9Scyw2tX4tEcAn9XZCHyTb2z6xlNi7sqZC7YU7ZCqjZBwi2070NMIBN2bCrIsgoPOMvZCsLhs5C0mUJ6RxLTM4RFPrIE2wtqPY1nPa6ZC1qYLCQsqvYV69zgZA8pTZC72ZBwf2l0Jt79jjxOpZCZB92RQD55XOQa3cH0o7xnerZB05s9tQMuhGZC1aofsi9VpWQGJE36ik6ngCSWrFu0prgMQfa7")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID", "1307957199078751")

# Configuración de Base de Datos (PostgreSQL en Render o SQLite local)
db_url = os.environ.get("DATABASE_URL", "sqlite:///quiniela.db")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==========================================
# MODELO DE LA BASE DE DATOS
# ==========================================
class Apuesta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    numero = db.Column(db.String(10), nullable=False)
    monto = db.Column(db.Float, nullable=False)

with app.app_context():
    db.create_all()

# ==========================================
# PLANTILLA HTML WEB (BOOTSTRAP 5)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quiniela en Línea - Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f4f6f9; }
        .card { border-radius: 12px; }
        .badge-numero { font-size: 1.1rem; padding: 0.4em 0.8em; }
    </style>
</head>
<body>
    <div class="container py-5">
        <div class="row justify-content-center mb-4">
            <div class="col-md-10 text-center">
                <h1 class="fw-bold text-primary display-5">🎲 Quiniela en Línea</h1>
                <p class="text-muted lead">Panel de control y registro de apuestas recibidas en tiempo real</p>
            </div>
        </div>

        <div class="row justify-content-center">
            <div class="col-md-10">
                <div class="card shadow-sm border-0">
                    <div class="card-header bg-dark text-white d-flex justify-content-between align-items-center py-3">
                        <h5 class="mb-0">📋 Registros de Apuestas</h5>
                        <span class="badge bg-primary">Total: {{ apuestas|length }}</span>
                    </div>
                    <div class="card-body p-0">
                        <div class="table-responsive">
                            <table class="table table-hover align-middle mb-0">
                                <thead class="table-light">
                                    <tr>
                                        <th class="ps-4"># ID</th>
                                        <th>Jugador</th>
                                        <th>Número Elegido</th>
                                        <th class="text-end pe-4">Monto Apostado</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for apuesta in apuestas %}
                                    <tr>
                                        <td class="ps-4 fw-bold text-secondary">#{{ apuesta.id }}</td>
                                        <td class="fw-bold">{{ apuesta.nombre }}</td>
                                        <td>
                                            <span class="badge bg-secondary badge-numero">{{ apuesta.numero }}</span>
                                        </td>
                                        <td class="text-end pe-4 fw-bold text-success fs-5">${{ "%.2f"|format(apuesta.monto) }}</td>
                                    </tr>
                                    {% else %}
                                    <tr>
                                        <td colspan="4" class="text-center text-muted py-5">
                                            📥 No hay apuestas registradas todavía. Envía un mensaje por WhatsApp para empezar.
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

# ==========================================
# RUTAS DE LA APLICACIÓN
# ==========================================

@app.route("/", methods=["GET"])
def index():
    apuestas = Apuesta.query.order_by(Apuesta.id.desc()).all()
    return render_template_string(HTML_TEMPLATE, apuestas=apuestas)

# Endpoint compatible tanto para /webhook como para /whatsapp
@app.route("/webhook", methods=["GET", "POST"])
@app.route("/whatsapp", methods=["GET", "POST"])
def webhook():

    # 1. VERIFICACIÓN GET (Meta Webhook setup)
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("--- WEBHOOK VERIFICADO EXITOSAMENTE ---")
            return challenge, 200
        print("--- ERROR DE VERIFICACIÓN: TOKEN INCORRECTO ---")
        return "Token inválido", 403

    # 2. PROCESAMIENTO POST (Recepción de mensajes de WhatsApp)
    elif request.method == "POST":
        data = request.get_json()

        try:
            entry = data.get("entry", [])[0]
            changes = entry.get("changes", [])[0]
            value = changes.get("value", {})
            messages = value.get("messages", [])

            if messages:
                msg = messages[0]
                from_number = msg.get("from")
                text_body = msg.get("text", {}).get("body", "").strip()

                print(f"Mensaje recibido de {from_number}: {text_body}")

                # Validar formato: "Nombre, Numero, Monto"
                partes = [p.strip() for p in text_body.split(",") if p.strip()]

                if len(partes) == 3:
                    nombre, numero, monto_str = partes[0], partes[1], partes[2]
                    
                    try:
                        monto = float(monto_str)
                        # Formatear el número a dos dígitos si ingresan '7' -> '07'
                        if len(numero) == 1 and numero.isdigit():
                            numero = f"0{numero}"

                        # Guardar en la base de datos
                        nueva_apuesta = Apuesta(nombre=nombre, numero=numero, monto=monto)
                        db.session.add(nueva_apuesta)
                        db.session.commit()

                        # Enviar confirmación por WhatsApp
                        respuesta_texto = f"✅ ¡Apuesta registrada!\n👤 Jugador: {nombre}\n🎲 Número: {numero}\n💵 Monto: ${monto:.2f}"
                        enviar_whatsapp(from_number, respuesta_texto)

                    except ValueError:
                        enviar_whatsapp(from_number, "⚠️ Error: El monto debe ser un número válido. Formato: Nombre, Numero, Monto")
                else:
                    enviar_whatsapp(from_number, "⚠️ Formato incorrecto. Por forma envía tu apuesta así:\nNombre, Numero, Monto\nEjemplo: Juan, 45, 500")

        except Exception as e:
            print(f"Error procesando mensaje: {e}")

        return jsonify({"status": "success"}), 200

# ==========================================
# FUNCIÓN AUXILIAR PARA ENVIAR WHATSAPP
# ==========================================
def enviar_whatsapp(to_phone, message):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "text",
        "text": {"body": message}
    }
    response = requests.post(url, json=payload, headers=headers)
    print(f"Respuesta de Meta API ({response.status_code}): {response.text}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import requests

app = Flask(__name__)

# Configuración de la base de datos SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiniela.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Definición del modelo (Tabla de Apuestas)
class Apuesta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jugador = db.Column(db.String(100), nullable=False)
    numero = db.Column(db.String(2), nullable=False)
    monto = db.Column(db.Float, nullable=False)

# Crear la base de datos automáticamente si no existe
with app.app_context():
    db.create_all()

# Plantilla HTML integrada con Bootstrap
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quiniela en Línea</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css">
</head>
<body class="bg-light">
    <div class="container mt-5">
        <div class="text-center mb-4">
            <h1 class="display-5 font-weight-bold text-primary">🎲 Quiniela en Línea 🎲</h1>
            <p class="text-muted">Apuestas guardadas de forma persistente en SQLite & WhatsApp</p>
        </div>

        <div class="row">
            <!-- Formulario de Apuesta -->
            <div class="col-md-5 mb-4">
                <div class="card shadow-sm">
                    <div class="card-body">
                        <h4 class="card-title mb-3">Nueva Apuesta</h4>
                        <form method="POST" action="/apostar">
                            <div class="form-group">
                                <label for="jugador">Nombre del Jugador:</label>
                                <input type="text" class="form-control" id="jugador" name="jugador" required placeholder="Ej: Juan Pérez">
                            </div>
                            <div class="form-group">
                                <label for="numero">Número (00 al 99):</label>
                                <input type="number" class="form-control" id="numero" name="numero" min="0" max="99" required placeholder="Ej: 45">
                            </div>
                            <div class="form-group">
                                <label for="monto">Monto a apostar ($):</label>
                                <input type="number" class="form-control" id="monto" name="monto" step="0.01" required placeholder="Ej: 500">
                            </div>
                            <button type="submit" class="btn btn-primary btn-block">Registrar Apuesta</button>
                        </form>
                    </div>
                </div>
            </div>

            <!-- Listado de Apuestas Realizadas -->
            <div class="col-md-7">
                <div class="card shadow-sm">
                    <div class="card-body">
                        <h4 class="card-title mb-3">Apuestas Registradas</h4>
                        {% if apuestas %}
                            <div class="table-responsive">
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>Jugador</th>
                                            <th>Número</th>
                                            <th>Monto</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for a in apuestas %}
                                        <tr>
                                            <td>{{ a.jugador }}</td>
                                            <td><span class="badge badge-success p-2" style="font-size: 1rem;">{{ a.numero }}</span></td>
                                            <td>${{ "%.2f"|format(a.monto) }}</td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        {% else %}
                            <p class="text-muted">Aún no hay apuestas registradas para este sorteo.</p>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

# Rutas web principales
@app.route('/')
def index():
    apuestas = Apuesta.query.order_by(Apuesta.id.desc()).all()
    return render_template_string(HTML_TEMPLATE, apuestas=apuestas)

@app.route('/apostar', methods=['POST'])
def apostar():
    jugador = request.form.get('jugador')
    numero = request.form.get('numero')
    monto = request.form.get('monto')
    
    if jugador and numero and monto:
        nueva_apuesta = Apuesta(
            jugador=jugador,
            numero=str(numero).zfill(2),
            monto=float(monto)
        )
        db.session.add(nueva_apuesta)
        db.session.commit()
        
    return redirect(url_for('index'))

# Configuración de WhatsApp Webhook y API
VERIFY_TOKEN = "mi_token_secreto_quiniela_123"
WHATSAPP_TOKEN = "EAAG..."
PHONE_NUMBER_ID = "106..."

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
        print(f"Error enviando mensaje de WhatsApp: {e}")
        return None

@app.route('/webhook', methods=['GET'])
def verificar_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode and token:
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print("¡Webhook verificado correctamente por Meta!")
            return challenge, 200
        else:
            return "Error de verificación: Token incorrecto", 403
    return "Parámetros faltantes", 400

@app.route('/webhook', methods=['POST'])
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
                        
                        print(f"Mensaje recibido de {numero_remitente}: {texto_mensaje}")
                        
                        # Formato esperado: Nombre, Numero, Monto (Ej: Juan, 45, 500)
                        partes = [p.strip() for p in texto_mensaje.split(',')]
                        
                        if len(partes) == 3:
                            jugador = partes[0]
                            numero = partes[1].zfill(2)
                            try:
                                monto = float(partes[2])
                                
                                nueva_apuesta = Apuesta(
                                    jugador=jugador,
                                    numero=numero,
                                    monto=monto
                                )
                                db.session.add(nueva_apuesta)
                                db.session.commit()
                                
                                respuesta = f"✅ ¡Apuesta registrada con éxito!\n👤 Jugador: {jugador}\n🎲 Número: {numero}\n💰 Monto: ${monto}"
                                enviar_mensaje_whatsapp(numero_remitente, respuesta)
                                
                            except ValueError:
                                enviar_mensaje_whatsapp(numero_remitente, "❌ Error: El monto debe ser un número válido. Usa el formato: Nombre, Número, Monto (Ej: Juan, 45, 500)")
                        else:
                            enviar_mensaje_whatsapp(numero_remitente, "⚠️ Formato incorrecto. Por favor envía tu apuesta usando este formato:\nNombre, Número, Monto\n(Ejemplo: Juan, 45, 500)")
                            
            return "EVENT_RECEIVED", 200
    except Exception as e:
        print(f"Error procesando el webhook: {e}")
        
    return "OK", 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
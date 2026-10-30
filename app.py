from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import requests

app = Flask(__name__)

# Configuración de base de datos dinámica (SQLite local / PostgreSQL en Render)
database_url = os.environ.get("DATABASE_URL")
if database_url:
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
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

# ==========================================
# Plantilla HTML MEJORADA CON DISEÑO MODERNO
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quiniela Premium :: Tu Suerte en Línea</title>
    <!-- Bootstrap 4.5 -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css">
    <!-- FontAwesome para Iconos -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
    
    <style>
        body {
            font-family: 'Poppins', sans-serif;
            background-color: #f0f2f5;
        }
        .navbar-custom {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .navbar-brand {
            font-weight: 700;
            color: white !important;
            letter-spacing: 1px;
        }
        .hero-banner {
            background: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), url('/static/quini429.jpg');
            background-size: cover;
            background-position: center;
            color: white;
            padding: 100px 0;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        .hero-banner h1 {
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        .card {
            border: none;
            border-radius: 15px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.1) !important;
        }
        .card-title {
            font-weight: 600;
            color: #1e3c72;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .form-control {
            border-radius: 10px;
            padding: 12px 15px;
            border: 1px solid #ced4da;
        }
        .form-control:focus {
            box-shadow: 0 0 0 0.2rem rgba(30, 60, 114, 0.25);
            border-color: #2a5298;
        }
        .input-group-text {
            background-color: #f8f9fa;
            border-radius: 10px 0 0 10px;
            border-right: none;
            color: #2a5298;
        }
        .input-group .form-control {
            border-radius: 0 10px 10px 0;
        }
        .btn-gradient {
            background: linear-gradient(135deg, #2a5298 0%, #1e3c72 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 12px 20px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: background 0.3s ease;
        }
        .btn-gradient:hover {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        }
        .table {
            border-collapse: separate;
            border-spacing: 0 10px;
        }
        .table thead th {
            border: none;
            color: #6c757d;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85rem;
        }
        .table tbody tr {
            background-color: white;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            border-radius: 10px;
        }
        .table tbody td {
            border: none;
            padding: 20px;
            vertical-align: middle;
        }
        .table tbody tr td:first-child {
            border-radius: 10px 0 0 10px;
        }
        .table tbody tr td:last-child {
            border-radius: 0 10px 10px 0;
        }
        .badge-numero {
            background-color: #28a745;
            color: white;
            font-size: 1.2rem;
            font-weight: 700;
            padding: 10px 15px;
            border-radius: 50%;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .monto-text {
            font-weight: 600;
            color: #1e3c72;
            font-size: 1.1rem;
        }
        footer {
            margin-top: 50px;
            padding: 30px 0;
            background-color: #e9ecef;
            color: #6c757d;
        }
    </style>
</head>
<body>
    <!-- Barra de Navegación -->
    <nav class="navbar navbar-expand-lg navbar-custom">
        <div class="container">
            <a class="navbar-brand" href="#"><i class="fas fa-dice mr-2"></i>QUINIELA PREMIUM</a>
        </div>
    </nav>

    <div class="container mt-4">
        <!-- Hero Banner -->
        <div class="hero-banner text-center">
            <div class="container">
                <h1 class="display-4">¡Tu Próxima Jugada Ganadora!</h1>
                <p class="lead">Registrá tus apuestas de forma segura y seguí el sorteo en tiempo real.</p>
            </div>
        </div>

        <div class="row">
            <!-- Formulario de Apuesta Mejorado -->
            <div class="col-md-5 mb-4">
                <div class="card shadow">
                    <div class="card-body">
                        <h4 class="card-title"><i class="fas fa-plus-circle mr-2"></i>Nueva Apuesta</h4>
                        <form method="POST" action="/apostar">
                            <div class="form-group">
                                <label for="jugador">Nombre del Jugador</label>
                                <div class="input-group">
                                    <div class="input-group-prepend">
                                        <span class="input-group-text"><i class="fas fa-user"></i></span>
                                    </div>
                                    <input type="text" class="form-control" id="jugador" name="jugador" required placeholder="Ej: Juan Pérez">
                                </div>
                            </div>
                            <div class="form-group">
                                <label for="numero">Número a Jugar (00-99)</label>
                                <div class="input-group">
                                    <div class="input-group-prepend">
                                        <span class="input-group-text"><i class="fas fa-hashtag"></i></span>
                                    </div>
                                    <input type="number" class="form-control" id="numero" name="numero" min="0" max="99" required placeholder="Ej: 45">
                                </div>
                            </div>
                            <div class="form-group">
                                <label for="monto">Monto a Apostar ($)</label>
                                <div class="input-group">
                                    <div class="input-group-prepend">
                                        <span class="input-group-text"><i class="fas fa-dollar-sign"></i></span>
                                    </div>
                                    <input type="number" class="form-control" id="monto" name="monto" step="0.01" required placeholder="Ej: 500">
                                </div>
                            </div>
                            <button type="submit" class="btn btn-gradient btn-block mt-4">
                                <i class="fas fa-ticket-alt mr-2"></i>Registrar Apuesta
                            </button>
                        </form>
                    </div>
                </div>
            </div>

            <!-- Listado de Apuestas Realizadas -->
            <div class="col-md-7">
                <div class="card shadow">
                    <div class="card-body">
                        <h4 class="card-title"><i class="fas fa-history mr-2"></i>Apuestas Registradas</h4>
                        {% if apuestas %}
                            <div class="table-responsive">
                                <table class="table table-hover">
                                    <thead>
                                        <tr>
                                            <th>Jugador</th>
                                            <th class="text-center">Número</th>
                                            <th class="text-right">Monto</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for a in apuestas %}
                                        <tr>
                                            <td>
                                                <i class="fas fa-user-circle text-muted mr-2"></i>{{ a.jugador }}
                                            </td>
                                            <td class="text-center">
                                                <span class="badge-numero">{{ a.numero }}</span>
                                            </td>
                                            <td class="text-right monto-text">
                                                ${{ "%.2f"|format(a.monto) }}
                                            </td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        {% else %}
                            <div class="text-center py-5 text-muted">
                                <i class="fas fa-box-open fa-3x mb-3"></i>
                                <p>Aún no hay apuestas registradas para este sorteo.</p>
                            </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer class="text-center">
        <div class="container">
            <p class="mb-0">&copy; 2026 Quiniela Premium. Todos los derechos reservados.</p>
            <small>Sistema de gestión de apuestas persistente.</small>
        </div>
    </footer>

    <!-- Scripts de Bootstrap -->
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/js/bootstrap.min.js"></script>
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
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "quini123")
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
        print(f"Error enviando mensaje de WhatsApp: {e}")
        return None

# Lógica para procesar el webhook
def procesar_webhook_logic():
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

# Rutas para GET (Verificación de Meta)
@app.route('/webhook', methods=['GET'])
@app.route('/whatsapp', methods=['GET'])
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

# Rutas para POST (Recepción de mensajes de WhatsApp)
@app.route('/webhook', methods=['POST'])
@app.route('/whatsapp', methods=['POST'])
def recibir_mensajes():
    return procesar_webhook_logic()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
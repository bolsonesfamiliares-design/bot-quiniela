from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiniela.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Apuesta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jugador = db.Column(db.String(100), nullable=False)
    numero = db.Column(db.String(10), nullable=False)
    monto = db.Column(db.Float, nullable=False)

# Crear las tablas en la base de datos automáticamente al iniciar
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    apuestas = Apuesta.query.all()
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Quiniela - Apuestas</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; color: #333; }
            h1 { color: #0275d8; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; background: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            th, td { padding: 12px 15px; border: 1px solid #ddd; text-align: left; }
            th { background-color: #0275d8; color: white; }
            tr:nth-child(even) { background-color: #f9f9f9; }
        </style>
    </head>
    <body>
        <h1>🎲 Quiniela - Apuestas Registradas</h1>
        <table>
            <tr>
                <th>ID</th>
                <th>Jugador</th>
                <th>Número</th>
                <th>Monto ($)</th>
            </tr>
    """
    for a in apuestas:
        html += f"<tr><td>{a.id}</td><td>{a.jugador}</td><td>{a.numero}</td><td>${a.monto:.2f}</td></tr>"
    html += """
        </table>
    </body>
    </html>
    """
    return html

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print("📦 JSON recibido:", data)
    try:
        if data and data.get('object'):
            for entry in data['entry']:
                for change in entry['changes']:
                    value = change.get('value', {})
                    if 'messages' in value:
                        mensaje_info = value['messages'][0]
                        numero_remitente = mensaje_info['from']
                        texto_mensaje = mensaje_info['text']['body'].strip()
                        
                        print(f"✅ Mensaje detectado de {numero_remitente}: {texto_mensaje}")
                        
                        partes = [p.strip() for p in texto_mensaje.split(',')]
                        if len(partes) == 3:
                            jugador = partes[0]
                            numero = partes[1].zfill(2)
                            monto = float(partes[2])
                            
                            nueva_apuesta = Apuesta(jugador=jugador, numero=numero, monto=monto)
                            db.session.add(nueva_apuesta)
                            db.session.commit()
                            print("💾 ¡Apuesta guardada en la base de datos con éxito!")
                            
            return {"status": "EVENT_RECEIVED"}, 200
    except Exception as e:
        print(f"❌ Error procesando el webhook: {e}")
        
    return {"status": "OK"}, 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
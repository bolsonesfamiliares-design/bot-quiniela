from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Configuración de la base de datos SQLite
# Se guardará en un archivo llamado 'quiniela.db' en la raíz del proyecto
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
            <p class="text-muted">Apuestas guardadas de forma persistente en SQLite</p>
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

@app.route('/')
def index():
    # Consultar todas las apuestas ordenadas de la más reciente a la más antigua
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
            numero=str(numero).zfill(2), # Asegura formato de dos dígitos ej: '05'
            monto=float(monto)
        )
        db.session.add(nueva_apuesta)
        db.session.commit()
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
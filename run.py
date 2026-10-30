from app import app, db

if __name__ == '__main__':
    print("🚀 Iniciando servidor Flask para la Quiniela...")
    app.run(debug=True, port=5000)
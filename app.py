from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = "quiniela123"

@app.route('/', methods=['GET'])
def home():
    return "Bot de Quiniela activo en Render!", 200

@app.route('/whatsapp', methods=['GET'])
def verify():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode == 'subscribe' and token == VERIFY_TOKEN:
        return challenge, 200
    
    return 'Token de verificación inválido', 403

@app.route('/whatsapp', methods=['POST'])
def webhook():
    return "EVENT_RECEIVED", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

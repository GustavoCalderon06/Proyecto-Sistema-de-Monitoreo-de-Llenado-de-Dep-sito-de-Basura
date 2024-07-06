from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from flask_cors import CORS
from datetime import datetime
from flask_socketio import SocketIO, emit
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
from bson import ObjectId

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

# Configuración de la conexión a MongoDB
app.config["MONGO_URI"] = "mongodb://localhost:27017/Llenado_Basura"
mongo = PyMongo(app)
db = mongo.db

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return super(JSONEncoder, self).default(o)

app.json_encoder = JSONEncoder

def enviar_correo(subject, body, config):
    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls
    sender_email = config["cuenta_gmail"]
    receiver_email = config["cuenta_gmail"]
    password = config["contraseña"]

    mensaje = MIMEMultipart()
    mensaje['From'] = sender_email
    mensaje['To'] = receiver_email
    mensaje['Subject'] = subject
    mensaje.attach(MIMEText(body, 'plain'))

    context = ssl.create_default_context()

    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls(context=context)  # Secure the connection
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, mensaje.as_string())
        print("Correo electrónico enviado exitosamente.")
    except Exception as e:
        print(f"No se pudo enviar el correo electrónico. Error: {e}")
    finally:
        server.quit()

@app.route('/api/data', methods=['POST'])
def receive_data():
    data = request.json
    nivelLlenado = data.get('nivelLlenado')

    if (nivelLlenado is not None) and (0 <= nivelLlenado <= 100):
        entry = {
            'nivelLlenado': nivelLlenado,
            'timestamp': datetime.utcnow()
        }
        db.sensor_data.insert_one(entry)
        entry['_id'] = str(entry['_id'])
        entry['timestamp'] = entry['timestamp'].isoformat()
        socketio.emit('new_data', entry)

        if nivelLlenado >= 80:
            with open('config.json') as config_file:
                config = json.load(config_file)
                enviar_correo(
                    "Alerta: Depósito al 80% de capacidad",
                    f"El depósito ha alcanzado un nivel de llenado del {nivelLlenado}%. Es necesario vaciarlo para evitar desbordamientos.",
                    config
                )

        return jsonify({'message': 'Data received successfully!'}), 200
    else:
        return jsonify({'message': 'Invalid data!'}), 400

@app.route('/api/data', methods=['GET'])
def get_data():
    data = list(db.sensor_data.find().sort('timestamp', -1).limit(100))
    for entry in data:
        entry['_id'] = str(entry['_id'])
        entry['timestamp'] = entry['timestamp'].isoformat()
    return jsonify(data), 200

@app.route('/api/last_data', methods=['GET'])
def get_last_data():
    last_data = db.sensor_data.find_one(sort=[('timestamp', -1)])
    if last_data:
        last_data['_id'] = str(last_data['_id'])
        last_data['timestamp'] = last_data['timestamp'].isoformat()
        return jsonify(last_data), 200
    else:
        return jsonify({'message': 'No data found!'}), 404

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from flask_cors import CORS
from datetime import datetime
from flask_socketio import SocketIO, emit
import json
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

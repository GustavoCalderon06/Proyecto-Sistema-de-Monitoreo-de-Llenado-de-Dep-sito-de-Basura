from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from datetime import datetime

app = Flask(__name__)

# Configuración de MongoDB
app.config["MONGO_URI"] = "mongodb://localhost:27017/Llenado_Basura"  # Asegúrate de que MongoDB esté corriendo en tu servidor

mongo = PyMongo(app)
db = mongo.db

@app.route('/api/data', methods=['POST'])
def add_data():
    data = request.json
    data['timestamp'] = datetime.utcnow()
    db.sensor_data.insert_one(data)
    return jsonify({'message': 'Datos recibidos'}), 200

@app.route('/api/data', methods=['GET'])
def get_data():
    data = db.sensor_data.find().sort('timestamp', -1).limit(10)
    result = []
    for item in data:
        item['_id'] = str(item['_id'])
        result.append(item)
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)

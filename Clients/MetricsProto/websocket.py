import time
from flask_socketio import SocketIO, Namespace
from flask import Flask, jsonify


class TrackingNamespace(Namespace):
    def on_connect(self):
        print('Success Connection')
        self.send_initial_location()

    def send_initial_location(self):
        # Obtenha a última localização salva no banco de dados ou cache
        # Isso depende da sua implementação específica

        # Exemplo: obter a última localização de um dispositivo fictício
        last_location = {'latitude': -19.161327510050672, 'longitude': -22.94313713397682}

        # Emita a última localização para o cliente
        self.emit('location_update', last_location)


app_socketio = Flask(__name__)
socketio = SocketIO(app_socketio, cors_allowed_origins="*", logger=True, engineio_logger=True, namespace='/tracking')
socketio.on_namespace(TrackingNamespace)

if __name__ == '__main__':
    socketio.run(app_socketio, host='0.0.0.0', port=8082, debug=True, use_reloader=False, allow_unsafe_werkzeug=True)

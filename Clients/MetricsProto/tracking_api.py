from flask_cors import CORS
from flask_socketio import SocketIO
from flask import Flask, request, jsonify
import requests
from Clients.Db.database import Database
import grpc
import metrics_pb2
import metrics_pb2_grpc
from Clients.utils import haversine_distance
import time


def send_metrics(device_id, brand, distance):
    try:
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = metrics_pb2_grpc.MetricsServiceStub(channel)

            request = metrics_pb2.LocationMetricsRequest(
                device_id=device_id,
                brand=brand,
                distance=distance
            )

            response = stub.SaveLocationMetrics(request)

            if response.success:
                print("Metrics sent successfully.")
            else:
                print(f"Failed to send metrics. Error: {response.error_message}")

    except Exception as e:
        print(f"Error sending metrics: {str(e)}")


class TrackingAPI:
    def __init__(self, database, cache):
        self.app = Flask(__name__)
        CORS(self.app, origins='*')
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.db = database
        self.cache = cache

        # Device Endpoints
        @self.app.route('/add_device', methods=['POST'])
        def add_device():
            try:
                data = request.get_json()
                db_result = self.db.add_device(data)
                return jsonify({'message': 'Device added successfully'}), 200
            except ValueError as ve:
                return jsonify({'error': str(ve)}), 400
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/delete_device', methods=['POST'])
        def delete_device():
            try:
                data = request.get_json()
                device_code = data.get('device_code')  # Atualizado para device_code
                db_result = self.db.delete_device(device_code)
                return jsonify({'message': 'Device deleted successfully'}), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/update_device', methods=['POST'])
        def update_device():
            try:
                data = request.get_json()
                db_result = self.db.update_device(data)
                return jsonify({'message': 'Device updated successfully'}), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/get_location', methods=['GET'])
        def get_location():
            try:
                # Obtenha parâmetros da solicitação
                device_code = request.args.get('device_code')  # Atualizado para device_code
                from_date = request.args.get('from_date')
                to_date = request.args.get('to_date')

                # Consulta de localizações no banco de dados
                location_data = self.db.get_location_data(device_code, from_date,
                                                          to_date)  # Atualizado para device_code

                return jsonify({'location_data': location_data}), 200

            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/update_with_first', methods=['GET'])
        def update_with_first():
            try:
                response = requests.get('http://localhost:5003/queue/get_first')

                if response.status_code == 200:
                    device_info = response.json()
                    if self.db.is_active_device(device_info.get('device_code')):
                        self.db.save_location(device_info)
                        self.cache[device_info.get('device_code')] = {
                            'latitude': device_info.get('latitude'),
                            'longitude': device_info.get('longitude'),
                            'timestamp': time.time()
                        }

                        distance_calculated = haversine_distance(
                            device_info['latitude'],
                            device_info['longitude'],
                            self.cache[device_info['device_code']]['latitude'],
                            self.cache[device_info['device_code']]['longitude'],
                        )

                        # Chame a função para enviar métricas
                        send_metrics(
                            device_info.get('device_code'),
                            device_info.get('brand'),
                            distance_calculated
                        )

                        # Emita a nova localização para o WebSocket
                        self.socketio.emit('location_update', device_info, namespace='/tracking')
                        return jsonify(device_info), 200
                    else:
                        return jsonify({'message': 'device dont exist or not active'}), 400
                else:
                    return jsonify({'message': 'Failed to get first device location'}), 500

            except requests.RequestException as e:
                return jsonify({'message': f'Error while making request: {str(e)}'}), 500

        @self.app.route('/delete_device_history', methods=['POST'])
        def delete_device_history():
            try:
                data = request.get_json()
                device_code = data.get('device_code')  # Atualizado para device_code
                db_result = self.db.get_location_data(device_code)  # Atualizado para device_code
                if len(db_result) < 1:
                    return jsonify({'message': f'No location history to delete for device: {device_code}'}), 200

                db_result = self.db.delete_location_history(device_code)  # Atualizado para device_code
                return jsonify(db_result), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.socketio.on('connect', namespace='/tracking')
        def handle_connect():
            print('Success Conection')

    def run(self, host='0.0.0.0', port=8081):
        # Execute o aplicativo Flask-SocketIO com o servidor interno
        self.socketio.run(self.app, host=host, port=port, debug=True, use_reloader=False, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    db = Database()
    cache = {}
    api = TrackingAPI(db, cache)
    api.run()

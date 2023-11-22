from flask import Flask, request, jsonify
import logging


class DataAPI:
    def __init__(self):
        self.app = Flask(__name__)
        self.device_location_queue = []
        self.last_request_data = []

        @self.app.route('/queue/add_device_location', methods=['POST'])
        def add_to_queue():
            try:
                self.last_request_data = request.get_json()
                result = self.validate_request_data()

                if result.get('code') == 200:
                    self.device_location_queue.append(self.last_request_data)
                    logging.info(f"Added location to the queue. Queue size: {len(self.device_location_queue)}")
                    return jsonify({'message': 'Success'}), 200

            except ValueError as e:
                logging.error(f"Error processing request: {e}")
                result = {'message': str(e), 'code': 400}

            return jsonify({'message': result.get('message')}), result.get('code')

        @self.app.route('/queue/get_first', methods=['GET'])
        def get_first():
            if len(self.device_location_queue) > 0:
                return jsonify(self.device_location_queue.pop(0)), 200
            else:
                logging.warning('Queue is Empty!')
                return '', 204

    def validate_request_data(self):
        message = 'Success'
        code = 200
        if "device_code" not in self.last_request_data:
            message = 'device_code not found!'
            code = 400
        if "latitude" not in self.last_request_data:
            message = 'latitude not found!'
            code = 400
        if "longitude" not in self.last_request_data:
            message = 'longitude not found!'
            code = 400
        return {'message': message, 'code': code}

    def run(self, host='0.0.0.0', port=5003):
        logging.basicConfig(level=logging.INFO)
        self.app.run(host=host, port=port)


if __name__ == '__main__':
    api = DataAPI()
    api.run()

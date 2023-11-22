import grpc
import metrics_pb2
import metrics_pb2_grpc

def send_metrics(device_id, brand, distance):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = metrics_pb2_grpc.MetricsServiceStub(channel)

        request = metrics_pb2.LocationMetricsRequest(
            device_id=device_id,
            brand=brand,
            distance=distance
        )

        response = stub.SaveLocationMetrics(request)

        if response.success:
            print("Metrics sent and processed successfully.")
        else:
            print(f"Failed to send metrics. Error: {response.error_message}")

# Exemplo de uso
send_metrics("device123", "BrandX", 10.5)
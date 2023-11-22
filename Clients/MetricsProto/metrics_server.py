import grpc
from concurrent import futures
import logging
import metrics_pb2_grpc
import metrics_pb2
from Clients.Db.database import Database

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MetricsService(metrics_pb2_grpc.MetricsServiceServicer):
    def SaveLocationMetrics(self, request, context):
        device_id = request.device_id
        brand = request.brand
        distance = request.distance

        logger.info(f"Received metrics for device {device_id} - Brand: {brand}, Distance: {distance}")

        # Lógica para processar distância acumulada e incrementar posições
        try:
            db = Database()
            db.save_location_metrics(device_id, brand, distance)
            logger.info("Metrics processed and saved successfully.")
            return metrics_pb2.LocationMetricsResponse(success=True)
        except Exception as e:
            logger.error(f"Error processing metrics: {str(e)}")
            return metrics_pb2.LocationMetricsResponse(success=False, error_message=str(e))

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    metrics_pb2_grpc.add_MetricsServiceServicer_to_server(MetricsService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    logger.info("gRPC Server is running and waiting for metrics.")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()

import grpc
from concurrent import futures
import time
from grpc_reflection.v1alpha import reflection
import counter_pb2
import counter_pb2_grpc

class CounterServicer(counter_pb2_grpc.CounterServiceServicer):
    def __init__(self):
        self.count = 0

    def GetCount(self, request, context):
        self.count += 1
        return counter_pb2.CountResponse(count=self.count)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    counter_pb2_grpc.add_CounterServiceServicer_to_server(
        CounterServicer(), server)
    
    # Enable reflection for debugging
    SERVICE_NAMES = (
        counter_pb2.DESCRIPTOR.services_by_name['CounterService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started on port 50051")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
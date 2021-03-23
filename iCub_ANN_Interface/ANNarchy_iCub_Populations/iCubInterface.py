import iCub_ANN_Interface.grpc.icub_pb2 as icub_pb2
import iCub_ANN_Interface.grpc.icub_pb2_grpc as icub_pb2_grpc


class iCubInputInterface(icub_pb2_grpc.ProvideInputServicer):
    """
    Setup gRPC client
    """

    def __init__(self, ip_address, port):
        
        self._ip_address = ip_address
        self._port = port

    def create_and_connect(self):
        """
        Create a gRPC socket and connect
        """
        pass

class iCubOutputInterface(icub_pb2_grpc.WriteOutputServicer):
    """
    Setup gRPC client
    """

    def __init__(self, ip_address, port):
        
        self._ip_address = ip_address
        self._port = port

    def create_and_connect(self):
        """
        Create a gRPC socket and connect
        """
        pass
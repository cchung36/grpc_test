import grpc
import time
from concurrent import futures

import data_pb2
import data_pb2_grpc

class DataServer(data_pb2_grpc.DataProcessorServicer):
    def ComputeData(self, request, context):
        worker_index=request.worker_index
        data=data_pb2.Data()
        print("Received Worker#{} compute request".format(worker_index))
        for i in range(3):
            data.trajectories.add(x=float(i+worker_index),y=float(i+1+worker_index))
            data.rewards.append(i+worker_index)
        data.worker_index=worker_index
        self.SaveDataToDB(data,worker_index)

        return data

    def SaveDataToDB(self,data,worker_index):
        db_channel=grpc.insecure_channel('db:50052')
        db_stub=data_pb2_grpc.DatabaseStub(db_channel)

        db_reply=db_stub.SaveData(data)

        print("WorkerID#{}: {} and {} data is saved".format(worker_index,db_reply.key[0],db_reply.key[1]))

if __name__ == '__main__':
    server=grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    data_pb2_grpc.add_DataProcessorServicer_to_server(DataServer(),server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print('server started...')
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        server.stop(0)
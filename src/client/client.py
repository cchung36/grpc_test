import grpc 
import time

from concurrent import futures

import data_pb2
import data_pb2_grpc

def client(worker_index):
    channel=grpc.insecure_channel('server:50051')
    stub=data_pb2_grpc.DataProcessorStub(channel)

    db_channel=grpc.insecure_channel('db:50052')
    db_stub=data_pb2_grpc.DatabaseStub(db_channel)

    data=stub.ComputeData(data_pb2.ComputeRequest(worker_index=worker_index))
    for i in range(len(data.rewards)):
        print("WorkerID:{},X:{},Y:{},Rewards:{}".format(worker_index,data.trajectories[i].x,data.trajectories[i].y,data.rewards[i]))

    db_request=data_pb2.DatabaseRequest()
    db_request.key.extend(['rewards','trajectory'])

    db_request.worker_index=worker_index

    db_data=db_stub.GetData(db_request)
    
    for i in range(len(db_data.rewards)):
        print("Database Data Recieved: WorkerID:{},X:{},Y:{},Rewards:{}".format(worker_index,db_data.trajectories[i].x,db_data.trajectories[i].y,db_data.rewards[i]))

if __name__ == '__main__':
    executor=futures.ThreadPoolExecutor(max_workers=10)
    for i in range(10):
        executor.submit(client,i)
    executor.shutdown()
    print('Exit')
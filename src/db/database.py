import grpc
import json
import time
import redis
import subprocess
import os

from concurrent import futures

import data_pb2
import data_pb2_grpc

class DatabaseServer(data_pb2_grpc.DatabaseServicer):
    def __init__(self):
        self.db=redis.StrictRedis(host="redis")
        self.db.flushdb()
        
        try:
            self.db.ping()
        except redis.ConnectionError:
            print("Connection failed")

    def SaveData(self, request, context):
        print("Database received save request")
        trajectories = []

        for i in range(len(request.rewards)):
            trajectories={"x":request.trajectories[i].x,"y":request.trajectories[i].y}
            self.db.rpush('rewards'+str(request.worker_index),request.rewards[i])
            json_trajectories=json.dumps(trajectories)        
            self.db.rpush('trajectory'+str(request.worker_index),json_trajectories)
        
        print("Data is saved in database")

        reply=data_pb2.DatabaseReply()
        reply.key.extend(['rewards','trajectory'])

        return reply

    def GetData(self, request, context):
        keys=[]
        data_db=[]
        data=data_pb2.Data()

        print("Database received retrieve request")

        for item in request.key:
            keys.append(item+str(request.worker_index))
            data_db.append(self.db.lrange(item+str(request.worker_index),0,-1))

        for item in keys:
            idx=keys.index(item)
            if keys[idx] == 'rewards'+str(request.worker_index):
                for item in data_db[idx]:
                    data.rewards.append(int(item))
            elif keys[idx] == 'trajectory'+str(request.worker_index):
                for item in data_db[idx]:
                    trajectory=json.loads(item)
                    data.trajectories.add(x=trajectory['x'],y=trajectory['y'])
            else:
                pass

        return data

if __name__ == "__main__":
    server=grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    data_pb2_grpc.add_DatabaseServicer_to_server(DatabaseServer(),server)
    server.add_insecure_port('[::]:50052')
    server.start()
    print('database server started...')
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        server.stop(0)
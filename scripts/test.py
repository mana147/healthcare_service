import websockets
from websockets import WebSocketServerProtocol
import asyncio

from threading import Thread
import threading
import time

# ======================================================
List_Clients = [WebSocketServerProtocol, WebSocketServerProtocol]

class WSC_Server:

    def __init__(self, ip, port):
        # self.List_Clients
        self.loop = asyncio.get_event_loop()
        self._client_timeout = 1
        self._wake_up_task = None
        self.ip = ip
        self.port = port
        self.mess = ''
        self.full_client = 3
        self.list_provider = []
        self.buffer = []
        # self.ws_server = websockets.serve(self.connect_client, self.ip, self.port)
    # ======================================================

    def keep_alive_handle(self):
        check_pass = 'hello client'
        while True:
            for countClients in List_Clients:
                # await countClients.send("fdgd")
                print(countClients)
                if countClients !=  0:
                    countClients.send(check_pass)
            time.sleep(3)

    # ======================================================

    def Listen(self):
        print("listening on {}:{}".format(self.ip, self.port))
        
        self.ws_server = websockets.serve(self.connect_client, self.ip, self.port)

        self.loop.run_until_complete(self.ws_server)

        # self._wake_up_task = asyncio.ensure_future(test())

        # keep_alive_task = threading.Thread(target=self.keep_alive_handle)
        
        # keep_alive_task.start()


        try:
            self.loop.run_forever()
        except :
            print (' ! keyboard interrupt ! ')
            # self.exit()
    
    # ======================================================
    
    async def connect_client(self, client: WebSocketServerProtocol, path):
        List_Clients[0] = client
        print('new client connected from {}:{}'.format(*client.remote_address))
        # print(self.list_clinets)
        # print(len(self.list_clinets))

        # check full client : if list client > 1000 client

        if len(List_Clients) > self.full_client:
            print ('full client')
            await self.disconnect_client(client)

        else:
            keep_alive_task = asyncio.ensure_future(self.keep_alive(client))
            asyncio.ensure_future(self.handle_authen(client))

            try:
                await self.handle_messages(client)
            except websockets.ConnectionClosed:
                keep_alive_task.cancel()
                await self.disconnect_client(client)

    # ======================================================
    
    async def handle_messages(self, client):
        print('handle_messages')
        while True:
            self.mess = await client.recv()
            # print( type (await client.recv()) ) 

            # print('recieved message from {}:{}: {}'.format(
            #     *client.remote_address, self.mess))

            # await asyncio.wait([client.send(self.mess) for client in self.clients]
     
    # ======================================================

    
            
    # ======================================================

    async def handle_authen(self, client):
        #  check messages == pass
        #  str = gửi pass : 
        #  sau 3 lần gửi  : nếu không có gửi trời lại thì đóng kết nối
        # còn nếu có pass : check messages , 
        #  nếu sai : đóng kết nối  và gửi clone connect 
        # nếu đúng : ghi id vào provider 

        check_pass = 'check : id'
        check = 'itc@12345'
        n = 0
        while (n < 5) :
            n = n + 1
            #  ngắt 1 s
            await asyncio.sleep(1)
            #  đợi gửi mess cho client
            await client.send(check_pass)
            #  kiểu tra xem có đúng pass chưa

            print(self.mess)

            if self.mess == check:
                print("check id ok")
                await client.send('check id ok')
                # self.mess.clear()
    
            
        # await client.close()
        print('out')
            # if len(self.mess) > 0:
            #     print('mes : {}'.format(self.mess))   

            #     # print('len : {}'.format(len(self.mess)))
            #     await client.send(self.mess)

            # await asyncio.sleep(self._client_timeout)

            # print('mes : {}'.format(self.mess))

 

    # ======================================================

    async def disconnect_client(self, client):
        # self.clients.remove(client)
        self.list_clinets.remove(client.remote_address)
        print('client {}:{} disconnected'.format(*client.remote_address))
        await client.close()
    
    # ======================================================
    async def keep_alive(self, client: WebSocketServerProtocol):
        n = 0
        while True:
            n = n + self._client_timeout
            await asyncio.sleep(self._client_timeout)
            try:
                print('pinging {}:{}'.format( *client.remote_address))
                await asyncio.wait_for(client.ping(), self._client_timeout)
                # await client.send(check_pass + str(n))

            except asyncio.TimeoutError:
                print('client {}:{} timed out'.format( *client.remote_address))
                await self.disconnect_client(client)

    # ======================================================
    def exit(self):
        print("exiting")
        # self._wake_up_task.cancel()
        try:
            self.loop.run_until_complete(self._wake_up_task)
        except asyncio.CancelledError:
            self.loop.close()

     # ===================================================

# ======================================================
async def test():
    n = 0 
    while True:
        n = n + 1
        print ('test > {} s '.format(n))
        await asyncio.sleep(1)

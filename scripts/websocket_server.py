import websockets
from websockets import WebSocketServerProtocol
import asyncio

# ======================================================

class WSC_Server:

    def __init__(self, ip, port):
        self.clients = set()
        self.list_clinets = []
        self.loop = asyncio.get_event_loop()
        self._client_timeout = 1
        self._wake_up_task = None
        self.ip = ip
        self.port = port
        self.mess = []
        self.full_client = 3

    # ======================================================

    def Listen(self):
        print("listening on {}:{}".format(self.ip, self.port))
        
        ws_server = websockets.serve(self.connect_client, self.ip, self.port)

        self.loop.run_until_complete(ws_server)

        # self._wake_up_task = asyncio.ensure_future(test())

        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            print ('caught keyboard interrupt')
            # self.exit()
    
    # ======================================================
    
    async def connect_client(self, client: WebSocketServerProtocol, path):
        self.clients.add(client)
        self.list_clinets.append(client.remote_address)

        print('new client connected from {}:{}'.format(*client.remote_address))
        print(self.list_clinets)
        print(len(self.list_clinets))

        if len(self.list_clinets) > self.full_client:
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
        while True:
            self.mess = await client.recv()

            # print('recieved message from {}:{}: {}'.format(
            #     *client.remote_address, self.mess))

            # await asyncio.wait([client.send(self.mess) for client in self.clients]
     
    # ======================================================

    
            
    # ======================================================
    async def handle_authen(self, client):
        # 

        while True:
            await asyncio.sleep(0.00000000001)
            if len(self.mess) > 0:
                print('mes : {}'.format(self.mess))
                print('len : {}'.format(len(self.mess)))

                await client.send(self.mess)

                self.mess = ''

            # await asyncio.sleep(self._client_timeout)

            # print('mes : {}'.format(self.mess))
            # 
            # self.mess = ''
 

    # ======================================================

    async def disconnect_client(self, client):
        self.clients.remove(client)
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
                await client.send(str(n))

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

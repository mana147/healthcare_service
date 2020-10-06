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
        self.mess =''
        self.full_client = 3
        self.list_clinets_provider = []
        self.authen: object
        self.status_check = True

    # ======================================================

    def Listen(self):
        print("listening on {}:{}".format(self.ip, self.port))
        
        ws_server = websockets.serve(self.connect_client, self.ip, self.port)
        # self.loop.run_until_complete(ws_server)

        asyncio.ensure_future(ws_server)

        # self._wake_up_task = asyncio.ensure_future(test())

        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            print ('caught keyboard interrupt')
            # self.exit()
    
    # ======================================================
    
    async def connect_client(self, client: WebSocketServerProtocol, path):
        self.status_check = True
        
        self.clients.add(client)
        self.list_clinets.append(client.remote_address)

        print('new client connected from {}:{}'.format(*client.remote_address))
        # print(self.list_clinets)
        print('số lượng client kết nối : {} \nlist client đang kết nối : {} '.format (len(self.list_clinets) , self.list_clinets ) )

        # check full client
        if len(self.list_clinets) > self.full_client:
            print ('full client ')
            await self.disconnect_client(client)
        else:
            # keep_alive_task = asyncio.ensure_future(self.keep_alive(client))
            authen =  asyncio.ensure_future(self.send_authen_check(client))
            # asyncio.ensure_future(self.authen_check(client))
            asyncio.ensure_future(self.handle_provider(client))
            asyncio.ensure_future(self.controll_handle(client))      
                
            try:
                await asyncio.ensure_future(self.handle_messages_input(client, authen))
            except :
                # keep_alive_task.cancel()
                await self.disconnect_client(client)
            finally:
                print('> disconnect_client ')
        

    # ======================================================
    # ====================================================== 

    async def handle_messages_input(self, client, authen):
        async for mess in client:
            # self.mess = mess 
            print('client {} messages :  {}'.format(client.remote_address, mess))

            # await self.authen_check(client, mess, authen)

            if self.status_check == True:
                await self.authen_check(client, mess, authen)


        # while True:
        #     self.mess = await client.recv()

            # print('recieved message from {}:{}: {}'.format(
            #     *client.remote_address, self.mess))

            # await asyncio.wait([client.send(self.mess) for client in self.clients]            
    # ======================================================
    async def send_authen_check(self, client):
        check_pass = 'pass id ? '
        for x in range(5):
            await asyncio.sleep(1)
            await client.send(check_pass)

        await client.send('fail')
        await self.disconnect_client(client)

    # ======================================================
    #  check messages == pass
    #  str = gửi pass :
    #  sau 3 lần gửi  : nếu không có gửi trời lại thì đóng kết nối
    # còn nếu có pass : check messages ,
    #  nếu sai : đóng kết nối  và gửi clone connect
    # nếu đúng : ghi id vào provider

    async def authen_check(self, client, mess, authen):
        if mess == 'Itc@12345':
            print('pass')
            await client.send('pass')
            self.status_check = False 
            authen.cancel()

            self.list_clinets_provider.append(client.remote_address)
        else:
            print('fail')
            await client.send('fail')
            try:
                await client.close()
            except:
                print('client {} disconnected'.format(client.remote_address))
        
    # ======================================================
    # client pulls data 
    # ghi data vao trong database

    async def handle_provider(self, client ):
        while True:
            await asyncio.sleep(3)

    # ======================================================

    async def disconnect_client(self, client):
        self.clients.remove(client)
        self.list_clinets.remove(client.remote_address)
        # self.list_clinets_provider.remove()

        print('client {} disconnected'.format(client.remote_address))

        await client.close()
    
    # ======================================================
    async def keep_alive(self, client: WebSocketServerProtocol):
        n = 0 
        while True:
            n = n + self._client_timeout
            await asyncio.sleep(self._client_timeout)
            try:
                # print('pinging {}:{}'.format( *client.remote_address))
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
    async def controll_handle(self, client):
        print('controll handle')
     # ===================================================

# ======================================================
async def test():
    n = 0 
    while True:
        n = n + 1
        print ('test > {} s '.format(n))
        await asyncio.sleep(1)

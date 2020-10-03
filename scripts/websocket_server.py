import websockets
from websockets import WebSocketServerProtocol
import asyncio

# ======================================================

class Server:
    def __init__(self, ip, port):
        self.clients = set()
        self.loop = asyncio.get_event_loop()
        self._client_timeout = 5
        self._wake_up_task = None
        self.ip = ip
        self.port = port 

    # ======================================================

    def Listen(self):
        print("listening on {}:{}".format(self.ip, self.port))
        
        ws_server = websockets.serve(self.connect_client, self.ip, self.port)

        self.loop.run_until_complete(ws_server)
        self._wake_up_task = asyncio.ensure_future(_wake_up())

        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            self.logger.debug('caught keyboard interrupt')
            self.exit()

    async def connect_client(self, client: WebSocketServerProtocol, path):
        self.clients.add(client)
        self.logger.info('new client connected from {}:{}'.format(
            *client.remote_address))
        keep_alive_task = asyncio.ensure_future(self.keep_alive(client))

        try:
            await self.handle_messages(client)
        except websockets.ConnectionClosed:
            keep_alive_task.cancel()
            await self.disconnect_client(client)

    async def handle_messages(self, client):
        while True:
            message = await client.recv()
            self.logger.info('recieved message from {}:{}: {}'.format(
                *client.remote_address, message))
            await asyncio.wait([client.send(message) for client in self.clients])

    async def disconnect_client(self, client):
        await client.close()
        self.clients.remove(client)
        self.logger.info('client {}:{} disconnected'.format(
            *client.remote_address))

    async def keep_alive(self, client: WebSocketServerProtocol):
        while True:
            await asyncio.sleep(self._client_timeout)
            try:
                self.logger.info('pinging {}:{}'.format(
                    *client.remote_address))
                await asyncio.wait_for(client.ping(), self._client_timeout)
            except asyncio.TimeoutError:
                self.logger.info('client {}:{} timed out'.format(
                    *client.remote_address))
                await self.disconnect_client(client)

    def exit(self):
        self.logger.info("exiting")
        self._wake_up_task.cancel()
        try:
            self.loop.run_until_complete(self._wake_up_task)
        except asyncio.CancelledError:
            self.loop.close()

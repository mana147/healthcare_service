import websockets
from websockets import WebSocketServerProtocol
import asyncio

import mysql.connector
import json
import bcrypt

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
        # ================================================
        self.check_True = '{"authen":"true"}'
        self.check_False = '{"authen":"false"}'
        self.check_Pass = '{"authen":"pass"}'
        self.check_Disconnect = '{"authen":"disconnect"}'
        self.check_Close = '{"authen":"close"}'
        self.check_Request_ID_PASSW = '{"authen":"request_pass"}'

        self.check_message_type = {
            "type": "request"
        }

        # =================================================


    # ======================================================

    def Listen(self):        
        print("listening on {}:{}".format(self.ip, self.port))
        
        ws_server = websockets.serve(self.connect_client, self.ip, self.port)
        asyncio.ensure_future(ws_server)

        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            print (' > keyboard interrupt')
            # self.exit()
    
    # ======================================================
    
    async def connect_client(self, client: WebSocketServerProtocol, path):
        # ======================================================
        # ======================================================
        
        self.status_check = True        
        self.clients.add(client)
        self.list_clinets.append(client.remote_address)

        print('new client connected from {}:{}'.format(*client.remote_address))
        # print(self.list_clinets)
        print('số lượng client kết nối : {} \nlist client đang kết nối : {} '.format(len(self.list_clinets), self.list_clinets))
        
        # ======================================================
        # ======================================================

        # check full client
        if len(self.list_clinets) > self.full_client:
            print ('full client ')
            await self.disconnect_client(client)
        else:
            # keep_alive_task = asyncio.ensure_future(self.keep_alive(client))
            authen =  asyncio.ensure_future(self.send_authen_check(client))
            # asyncio.ensure_future(self.handle_provider(client))
            # asyncio.ensure_future(self.controll_handle(client))      
                
            try:
                await asyncio.ensure_future(self.handle_messages_input(client, authen))
            except :
                # keep_alive_task.cancel()
                authen.cancel()
                await self.disconnect_client(client)
            finally:
                print('> end ')
        
    # ======================================================

    async def handle_messages_input(self, client, authen):
        async for mess in client:
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
    
    async def test(self, client, mess):
        n = 0 
        while True:
            n = n+1
            await asyncio.sleep(1)
            await client.send(str(n))

    # ======================================================
    # gửi 5 lần request đến client
    async def send_authen_check(self, client):
        try:
            for x in range(10):
                # sleep 1 s
                await asyncio.sleep(1)
                # gửi json request
                await client.send(self.check_Request_ID_PASSW)
                # print(x)
        
            # sau 5 lần request
            await client.send(self.check_False)
            # disconnect_client
            # await self.disconnect_client(client)

        except :
            print ("> close send authen check ")

    # ======================================================
    #  check messages == pass
    #  str = gửi pass :
    #  sau 3 lần gửi  : nếu không có gửi trời lại thì đóng kết nối
    # còn nếu có pass : check messages ,
    #  nếu sai : đóng kết nối  và gửi clone connect
    # nếu đúng : ghi id vào provider

    async def authen_check(self, client, mess, authen):
        
        # handle json 
        try:
            # chuyen mess sang dang json
            messJson = json.loads(mess)
            id_userhw_json = messJson["id_userhw"]
            password_json = messJson["password"]
            print('id = {}  \npassw = {}'.format(id_userhw_json, password_json))

        except:
            print("> Not json")


        # ============================================= 

        # val = self.Execute_sql(self.Select_table_user('users'))
        # print (val)
        #  handle sql
        try :
            data = self.Execute_sql(self.Select_id('users', 'id_userhw', id_userhw_json))
            # print(data)
            
            id_index_of_userhw = data[0][0]
            status_of_userhw = data[0][1]
            password_of_userhw = data[0][6]

            print (password_of_userhw)

        except:
            print('> Can not Execute_sql ')
            

        try:
            if bcrypt.checkpw(bytes(password_of_userhw, 'utf-8'), bytes(password_json, 'utf-8')):
                print("pass true")
            else:
                print("pass false")
        except:
            print ('> error')
            
        
        # ============================================
        # test database 
        # ===========================================
        # conver string to bytes
        # b_password_json = bytes(password_json, 'utf-8')
        # print(b_password_json)

        # truy vấn id_userhw trong database
        # try:
        #     cursor = mydb.cursor()

        #     cursor.reset()

        #     # cursor.execute(self.Select_id('users', 'id_userhw', id_userhw_json))
        #     sql = "SELECT * FROM users"
        #     cursor.execute(sql)``

        #     data = cursor.fetchall()
        #     print(data)

        #     cursor.close()
        
    
        # except :
        #     print('> search fail')
        # finally:
        #     password_of_userhw = 'error'

        # =======================================================
        #  nếu value_of_id_userhw không có data trả về => không có id_userhw trong database

        # try:
        #     if len(value_of_id_userhw) != 0 and bcrypt.checkpw(b_password_json, b_password_of_userhw) and status_of_userhw == 'offline':

        #         await client.send(self.check_Pass)
        #         # stop status_check 
        #         self.status_check = False
        #         authen.cancel()


        #         # print(value_of_id_userhw)

        #         # ======================================================
        #         self.list_clinets_provider.append(client.remote_address)
        #         # ======================================================
        #     else:
        #         print('fail')
        #         await client.send('clone connect')
        #         await self.disconnect_client(client)

        # except:
        #     print("fail")
        
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
                print('pinging {}:{}'.format( *client.remote_address))
                await asyncio.wait_for(client.ping(), self._client_timeout)
                # await client.send(str(n))

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
   
    async def controll_handle(self, client):
        print('controll handle')
     
    
    # =================================================== 
    # =================== My SQL ========================
    # ===================================================

    def config_mysql(self):
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="iot_database"
        )
        return mydb

    # ===================================================

    def Execute_sql(self, sql):
        mydb = self.config_mysql()
        cursor = mydb.cursor()

        cursor.execute(sql)
        
        data = cursor.fetchall()

        cursor.close()
        mydb.close()

        return data

    # ===================================================

    def Select_table_user(self,table_name):
        sql = "SELECT * FROM `" + table_name + "`"
        return sql

    # ===================================================

    def Select_id(self,table_name, column_name, value):
        list_column = 'id,status,active,id_userhw,name,number,password,email,level,user_enable'
        sql = 'SELECT ' + list_column + \
            ' FROM ' + table_name + \
            ' WHERE ' + column_name + ' LIKE ' + '"' + value + '"'
            
        return sql

    # ===================================================

    # def Update_status(self, table_name, column_name, value,index):
    #     # sql = "UPDATE `users` SET `status` = \'offline\' WHERE `users`.`id`
    #     sql = "UPDATE `{}` SET `{}` = \'{}\' WHERE `{}`.`{}` = {}" \
    #         .format(table_name)
    #     return sql
        
        


# ======================================================


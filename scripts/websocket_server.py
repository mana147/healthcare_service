# coding: utf-8
import websockets
from websockets import WebSocketServerProtocol
import asyncio

import mysql.connector
import json
import bcrypt

import datetime
import input.api_server as API


class WSC_Server:

    def __init__(self, ip, port):
        self.clients = set()
        self.list_clinets = []
        self.loop = asyncio.get_event_loop()
        self._client_timeout = 1
        self._wake_up_task = None
        self.ip = ip
        self.port = port
        self.mess = ''
        self.full_client = 5
        self.list_clinets_provider = []
        self.authen: object
        self.status_check = True

        self.dict_id_index_client = {}
        # ================================================

        # =================================================

    # ======================================================

    def Listen(self):
        print("listening on {}:{}".format(self.ip, self.port))

        ws_server = websockets.serve(self.connect_client, self.ip, self.port)
        asyncio.ensure_future(ws_server)

        try:
            self.loop.run_forever()
        except KeyboardInterrupt:

            for x in self.dict_id_index_client:
                print(x)
                var = self.dict_id_index_client[x]
                # update lại trạng thái offline khi đóng kết nôi
                self.Execute_sql_update(self.Update_status(
                    'users', 'status', 'id', str(var), 'offline'))
                # xóa buffer data khi đóng kết nối
                self.Execute_sql_update(self.Delete_data(
                    'buffer_sokhambenh', 'user_id', str(var)))

            print(' > keyboard interrupt')

            # self.exit()

    # ======================================================

    async def connect_client(self, client: WebSocketServerProtocol, path):
        # ======================================================
        # print(client)
        # ======================================================
        self.status_check = True
        self.clients.add(client)
        self.list_clinets.append(client.remote_address)

        print('new client connected from {}:{}'.format(*client.remote_address))
        # print(self.list_clinets)
        print('số lượng client kết nối : {} \nlist client đang kết nối : {} '.format(
            len(self.list_clinets), self.list_clinets))

        # ======================================================
        # ======================================================

        # check full client
        if len(self.list_clinets) > self.full_client:
            print('full client ')
            await self.disconnect_client(client)
        else:
            # keep_alive_task = asyncio.ensure_future(self.keep_alive(client))
            authen = asyncio.ensure_future(self.send_authen_check(client))
            # asyncio.ensure_future(self.handle_provider(client))
            # asyncio.ensure_future(self.controll_handle(client))

            # ======================================================================
            try:
                await asyncio.ensure_future(self.handle_messages_input(client, authen))
            except:
                # keep_alive_task.cancel()
                authen.cancel()
                await self.disconnect_client(client)

    # ======================================================

    async def handle_messages_input(self, client, authen):
        async for mess in client:
            # print('client {} messages :  {}'.format(client.remote_address, mess))
            # await self.authen_check(client, mess, authen)
            # print(self.status_check)

            if self.status_check == True:
                await self.authen_check(client, mess, authen)
            else:
                await self.handle_provide(client, mess)

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
                await client.send(API.api_request_id)
                # print(x)

            # sau 5 lần request
            await client.send(API.api_request_close)
            # disconnect_client
            await self.disconnect_client(client)

        except:
            print("> close send authen check ")

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
            if messJson['state'] == 'authen':
                id_userhw_json = messJson['data']['id']
                password_json = messJson['data']['password']
            else:
                await client.send(API.api_request_close)
                await self.disconnect_client(client)

            # print('id = {}  \npassw = {}'.format(id_userhw_json, password_json))

        except:
            await client.send(API.api_request_close)
            await self.disconnect_client(client)

        # =============================================

        # val = self.Execute_sql(self.Select_table_user('users'))
        # print (val)
        #  handle sql
        try:
            data = self.Execute_sql(self.Select_id(
                'users', 'id_userhw', id_userhw_json))
            # print(data)

            id_index_of_userhw = data[0][0]
            status_of_userhw = data[0][1]
            password_of_userhw = data[0][6]

            print('{} : {}'.format(id_index_of_userhw, status_of_userhw))

        except:
            print('> Can not Execute_sql ')

        # =======================================================
        #  nếu value_of_id_userhw không có data trả về => không có id_userhw trong database
        try:
            if len(data) != 0 and bcrypt.checkpw(bytes(password_json, 'utf-8'), bytes(password_of_userhw, 'utf-8')) and status_of_userhw == 'offline':
                await client.send(API.api_request_pass)
                self.status_check = False
                authen.cancel()

                # ======================================================
                #  update trạng thái online
                self.Execute_sql_update(self.Update_status(
                    'users', 'status', 'id', str(id_index_of_userhw), 'online'))

                # tạo buffer data trong buffer_sokhambenh
                self.Execute_sql_insert(self.Insert_data(
                    'buffer_sokhambenh', str(id_index_of_userhw)))

                # ======================================================

                print('{} = {}'.format(client.remote_address, id_index_of_userhw))

                buffer_dict = {
                    client.remote_address: id_index_of_userhw
                }
                self.dict_id_index_client.update(buffer_dict)

                # print(self.Update_status('users', 'status', 'id', '44', 'online'))
                # ======================================================

                # ======================================================
                self.list_clinets_provider.append(client.remote_address)
                # ======================================================
            else:
                await client.send(API.api_request_close)
                await self.disconnect_client(client)

        except:
            print("> ! fail")

    # ======================================================
    # client pulls data
    # ghi data vao trong database

    async def handle_provide(self, client, mess):
        try:
            # chuyen mess sang dang json
            messJson = json.loads(mess)

            # kiểm tra có đúng api gọi provider không
            if messJson['state'] == 'provide':

               # ======================================================
                
                if messJson['value'] == 'get_time':
                    x = datetime.datetime.now()
                    m = API.api_response_time(x.year, x.month, x.day, x.hour, x.minute, x.second)
                    await client.send(str(m))

                # ======================================================
                
                if messJson['value'] == 'push_sensor':
                    # print(messJson['data'])
                    var = self.dict_id_index_client[client.remote_address]
                    sql = self.Update_data(
                        'buffer_sokhambenh',
                        'user_id',
                        str(var),
                        messJson['data']['oxygen'],
                        messJson['data']['bloodpressure'],
                        messJson['data']['bodytemperature'],
                        messJson['data']['Heartbeat']
                    )
                    
                    try:
                        self.Execute_sql_update(sql)
                        await client.send(API.api_response_sensor_done)
                    except :
                        await client.send(API.api_response_sensor_fail)
                
                # ======================================================
                
                if messJson['value'] == 'get_sensor':
                    var = self.dict_id_index_client[client.remote_address]
                    sql = self.Select_data(
                        'buffer_sokhambenh',
                        'user_id',
                        str(var)
                    )

                    try:
                        data = self.Execute_sql(sql)[0]
                        # print(data)
                    except :
                        print("> error !")

                    m = API.api_response_sensor(
                        data[4],
                        data[5],
                        data[6],
                        data[7]
                    )
                    
                    await client.send(str(m))
                    
                # ======================================================
               
                if messJson['value'] == 'images':
                    pass

        except:
            await client.send(API.api_request_close)
            await self.disconnect_client(client)

        # await client.send(api.api_time)

    # ======================================================

    async def disconnect_client(self, client):
        self.clients.remove(client)
        self.list_clinets.remove(client.remote_address)
        # self.list_clinets_provider.remove()

        if (self.dict_id_index_client.get(client.remote_address) != None):
            var = self.dict_id_index_client[client.remote_address]
            self.dict_id_index_client.pop(client.remote_address)
            # update lại trạng thái offline khi đóng kết nôi
            self.Execute_sql_update(self.Update_status(
                'users', 'status', 'id', str(var), 'offline'))
            # xóa buffer data khi đóng kết nối
            self.Execute_sql_update(self.Delete_data(
                'buffer_sokhambenh', 'user_id', str(var)))

        # ======================================================
        print('client {} disconnected'.format(client.remote_address))
        await client.close()

    # ======================================================

    async def keep_alive(self, client: WebSocketServerProtocol):
        n = 0
        while True:
            n = n + self._client_timeout
            await asyncio.sleep(self._client_timeout)
            try:
                print('pinging {}:{}'.format(*client.remote_address))
                await asyncio.wait_for(client.ping(), self._client_timeout)
                # await client.send(str(n))

            except asyncio.TimeoutError:
                print('client {}:{} timed out'.format(*client.remote_address))
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

    def Execute_sql_update(self, sql):
        mydb = self.config_mysql()
        cursor = mydb.cursor()

        cursor.execute(sql)
        mydb.commit()

        cursor.close()
        mydb.close()

    def Execute_sql_insert(self, sql):
        mydb = self.config_mysql()
        cursor = mydb.cursor()

        cursor.execute(sql)
        mydb.commit()

        cursor.close()
        mydb.close()

    def Execute_sql_delete(self, sql):
        mydb = self.config_mysql()
        cursor = mydb.cursor()

        cursor.execute(sql)
        mydb.commit()

        cursor.close()
        mydb.close()

    # ===================================================

    def Select_table_user(self, table_name):
        sql = "SELECT * FROM `" + table_name + "`"
        return sql

    # ===================================================

    def Select_id(self, table_name, column_name, value):
        list_column = 'id,status,active,id_userhw,name,number,password,email,level,user_enable'
        sql = 'SELECT ' + list_column + \
            ' FROM ' + table_name + \
            ' WHERE ' + column_name + ' LIKE ' + '"' + value + '"'

        return sql

    # ===================================================

    def Update_status(self, table_name, column_name, id_, index, value):
        #  example sql = "UPDATE `users` SET `status` = \'online\' WHERE `users`.`id` = 44";
        sql = "UPDATE `"+table_name+"` SET `"+column_name+"` = '" + \
            value+"' WHERE `"+table_name+"`.`"+id_+"` = "+index+""
        return sql

    # ===================================================

    def Insert_data(self, table_name, user_id):
        sql = "INSERT INTO `{}`(`id`, `user_id`) VALUES(NULL, '{}')".format(
            table_name, user_id)
        return sql
    
    # ===================================================
    
    def Delete_data(self, table_name, column_name, user_id):
        sql = "DELETE FROM `buffer_sokhambenh` WHERE `{}`.`{}` = {}".format(table_name, column_name, user_id)
        return sql

    # ===================================================

    def Update_data(self, table_name, column_name, user_id, oxy, huyet_ap, nhiet_do, nhip_tim):
        sql = "UPDATE `{0}` SET `oxy` = '{3}', `huyet_ap` = '{4}', `nhiet_do` = '{5}', `nhip_tim` = '{6}' WHERE `{1}` = {2}".format(
            table_name, column_name, user_id, oxy, huyet_ap, nhiet_do, nhip_tim)
        return sql

    # ===================================================

    def Select_data(self, table_name, column_name, user_id ):
        sql = 'SELECT * FROM `{0}` WHERE `{1}` = {2}'.format(table_name, column_name, user_id)
        return sql

# ======================================================

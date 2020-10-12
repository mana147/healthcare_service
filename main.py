from scripts.websocket_server import WSC_Server
# import scripts.mysql_server as s_mysql


# ===================================================
# khởi tạo server

def main():
    WSC = WSC_Server('0.0.0.0', 443)
    WSC.Listen()
    
# ====================================================
if __name__ == '__main__':
    main()

    # ====================================================
    

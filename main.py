from app import create_app



app= create_app()



if __name__ == "__main__":
    # 本機測試
    app.run("127.0.0.1", 8080, debug=True, threaded=True)
    
    
    # 直接跑外網
    # *注意: 如果電腦已經有使用 80 port的軟體在運行，使用 80 port很有可能會導致衝突。
    # 但若改跑其他port(ex:8080 port)，則需要在網址中特別註明port參數才能夠訪問此伺服器(ex:http://127.0.0.1:8080)
    # *注意: 如果還是沒辦法的話，也有可能是被防火牆擋下來，可以試試在防火牆開起要使用的port看看
    
    # import socket
    # ip= socket.gethostbyname(socket.getfqdn(socket.gethostname()))
    # print("http://"+ ip)
    # app.run(ip, 80, debug=False, threaded=True)
    
    # 使用waitress內核來跑flask，會比原本flask內建的Werkzeug內核更穩定
    # from waitress import serve
    # serve(app, host="127.0.0.1", port=8080, threads=100)
    # serve(app, host=ip, port=80, threads=100)
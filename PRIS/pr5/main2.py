#https://iximiuz.com/ru/posts/writing-python-web-server-part-3/
from http_server import MyHTTPServer

if __name__ == '__main__':

  #HOWTO: http://127.0.0.1:8888/?id=3&vx=55

  host = "127.0.0.1"
  port =  8888
  name = "127.0.0.1"#"Robot Server"

  serv = MyHTTPServer(host, port, name)
  try:
    serv.serve_forever()
  except KeyboardInterrupt:
    pass
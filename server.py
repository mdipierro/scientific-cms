import os, uuid, threading
from bottle import request, Bottle, abort, static_file
from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketError
from geventwebsocket.handler import WebSocketHandler
from spreadsheet import Spreadsheet


app = Bottle()
sheets = {}
clients = {}
lock = threading.Lock()

def safely(func):
    try: return func()
    except: return None

def locked(func):
    lock.acquire()
    try: return func()
    finally: lock.release()

@app.route('/static/<path:path>')
def static(path):
    return static_file(path, root='static')

@app.route('/websocket/<name>')
def handle_websocket(name):
    # assign a uuid to the client
    client_id = str(uuid.uuid4()) 
    print client_id,name,'websocket connected'
    # request the websocket
    ws = request.environ.get('wsgi.websocket')
    if not ws:
        abort(400, 'Expected WebSocket request.')
    clients[client_id] = ws
    # create the spreadsheet if does not exist
    locked(lambda: name in sheet or sheets.update({name: Spreadsheet(name)}))
    # look and process changes to the spreadsheet
    while ws.socket is not None:
        changes = safely(lambda: json.loads(ws.receive()))
        if changes == None: return
        changes = locked(lambda: sheets[name].process(changes))
        for ows in clients.values:
            safely(lambda: ows.send(json.dumps(changes)))

def main():
    server = WSGIServer(("127.0.0.1", 8000), app, handler_class=WebSocketHandler)
    server.serve_forever()

if __name__ == '__main__': main()

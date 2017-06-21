import os, uuid, json, time, ast
from bottle import request, Bottle, abort, static_file
from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketError
from geventwebsocket.handler import WebSocketHandler
from spreadsheet import Spreadsheet
from trivial_tools import safely, get_locker

app = Bottle()
sheets = {}
clients = {}
locker = get_locker()

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
    locker(lambda: name in sheets or sheets.update({name: Spreadsheet(name)}))
    # look and process changes to the spreadsheet
    print 'here',sheets[name]
    while True:
        try:
            raw_data = ws.receive()
        except:
            break
        data = safely(lambda: json.loads(raw_data))
        if not data: 
            time.sleep(1)
            print 'sleeping'
            continue
        print data
        if 'code' in data:
            context = {}
            exec(data['code'], {}, context) # NOT SAFE CHECK THIS HERE
            sheets[name].context = context
        changes = data['formulas']
        if changes == None: return
        for key in changes.keys():
            if not changes[key] == '=':
                safely(lambda: changes.update({key:ast.literal_eval(changes[key])}))
        changes = locker(lambda: sheets[name].process(changes))
        ws.send(json.dumps(changes))
        
        #for ows in clients.values():
        #    safely(lambda: ows.send(json.dumps(changes)))

def main():
    server = WSGIServer(("127.0.0.1", 8000), app, handler_class=WebSocketHandler)
    server.serve_forever()

if __name__ == '__main__': main()

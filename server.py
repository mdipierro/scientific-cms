import os
import uuid
import json
import time
import ast

from bottle import request, Bottle, abort, static_file
from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketError
from geventwebsocket.handler import WebSocketHandler

from spreadsheet import Spreadsheet
from widgets import render
from trivial_tools import safely, get_locker
import pages

app = Bottle()
sheets = {}
clients = {}
locker = get_locker()

@app.route('/static/<path:path>')
def static(path):
    return static_file(path, root='static')

@app.route('/pages/search')
def search():
    items = pages.search(request.query['keywords'].split())
    return {'status':'success', 'data':'items'}

@app.route('/pages/<name>', method="GET")
def get_page(name):
    item = pages.retrieve(name)
    return {'status':'success', 'data':'item'}

@app.route('/pages/<name>', method="POST")
def post_page(name):    
    pages.store(id=name, title=request.json['title'], markup=request.json['markup'], code=request.json['code'])
    return {'status':'success'}

@app.route('/websocket')
def handle_websocket():
    # assign a uuid to the client
    client_id = str(uuid.uuid4()) 
    print client_id,'websocket connected'
    # request the websocket
    ws = request.environ.get('wsgi.websocket')
    if not ws:
        abort(400, 'Expected WebSocket request.')
    clients[client_id] = ws
    state = None
    while True:        
        try:
            raw_msg = ws.receive()
        except:
            break
        msg = safely(lambda: json.loads(raw_msg))        
        if not msg:
            time.sleep(0.1)
            continue  
        print 'msg:', msg
        command = msg.get('command')        
        # {command: "search", keywords: "hello world"}
        if command == 'search': 
            keywords = msg['keywords'].split()
            items = pages.search(keywords)
            ws.send(json.dumps({'command':'search-results', 'items':items}))
        # {command: "open", id: "r18r4g18734tr1087t"}
        elif command == 'open': 
            id = msg['id']
            locker(lambda: id in sheets or sheets.update({id: Spreadsheet(id)}))
            page = pages.retrieve(id) or {'id':id, 'title':'new page', 'markup':'', 'code':''}
            ws.send(json.dumps({'command':'page', 'page':page}))
        # {command: "compute", id: "..." code: "...", formulas: {..}}
        elif command == 'compute':
            id = msg['id']
            if not id in sheets: continue
            sheet = sheets[id]
            if 'code' in msg:
                context = {}
                try:
                    exec(msg['code'], {}, context) # NOT SAFE CHECK THIS HERE
                    sheets[id].context = context
                except:
                    pass
            changes = msg['formulas']
            if changes == None: return
            for key in changes.keys():
                if not changes[key] == '=':
                    safely(lambda: changes.update({key:ast.literal_eval(changes[key])}))
            changes = locker(lambda: sheets[id].process(changes))
            values = {key:render(value) for key, value in changes['values'].iteritems()}
            ws.send(json.dumps({'command':'values', 'values':values}))
        # {command: "save", page: {id:..., title:..., markup:..., code:...} }
        elif command == 'save':
            pages.store(**msg['page'])

def main():
    server = WSGIServer(("127.0.0.1", 8000), app, handler_class=WebSocketHandler)
    server.serve_forever()

if __name__ == '__main__': main()

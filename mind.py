import rethinkdb as r
import re
import json
import ulid
import ast

strings = re.compile('((\w+\__)?\w+)')

def load_value(data):
    return json.loads(data)

def dump_value(data):
    return json.dumps(data)

def safely(func, default=None):
    try:
        return func()
    except:
        return default

def init_db():
    r.connect( "localhost", 28015).repl()
    safely(lambda:r.db(dbname).table_create("pages").run())
    safely(lambda:r.db(dbname).table_create("cells").run())
    
def makeup_data():
    r.table("pages").delete().run()
    r.table("cells").delete().run()
    page_id = ulid.ulid()
    r.table("pages").insert({'id': page_id,
                             'markup': 'MARKUP',
                             'html': 'HTML',
                             'code': 'from math import *'}).run()
    for cell in [{'page_id':page_id, 'id':page_id+'__A1', 'value': 1, 
                  'input': '1', 'error': None, 'next':['A3']},
                 {'page_id':page_id, 'id':page_id+'__A2', 'value': 1, 
                  'input': '1', 'error': None, 'next':['A3']},
                 {'page_id':page_id, 'id':page_id+'__A3', 'value': 2, 
                  'input': '=A1+sin(A2)', 'error':None, 'next':[]}]:
        r.table("cells").insert(cell).run()
        
def onchange(record):
    if record['old_val']['input'] != record['new_val']['input']:
        cell = record['new_val']        

def recompute(cell):
    if cell['input'][0]=='=':
        page = r.table("pages").filter(r.row['id']==cell['page_id'])
        code = page['code']
        context = {}
        try:
            exec(code,{},context)
        except:
            cell['error'] = traceback.format_exc()
        else:
            symbols = set(strings.findall(cell['input'])) - set(context.keys())
            symbols = map(lambda s if '__' in sd else cell['page_id']+'__'+s, symbols)
            for other in r.table("cells").get(symbol).run():
                if other['error']:
                    cell['error'] = 'propagated'
                    value = load_value(other['value'])
                    context[symbol] = value
                    if symbol.startwith(page_id+'__'):
                        context[symbol.split('__',1)[1]] = value
            try:
                cell['value'] = dump_value(eval(cell['input'][1:],{},context))
                cell['error'] = None
            except:
                cell['error'] = traceback.format_exc()
    else:
        value = safely(lambda: ast.literal_eval(cell['input']), cell['input'])
        cell['value'] = dump_value(value)
        cell['error'] = None

    # nope this does not work because of graph....
    for cell_id in cell['next']:
        if not '__' in cell_id:
            cell_id = page_id+'__'+cell_id
        cell = r.table('cells').get(cell_id)
        recompute(cell)

    #cursor = r.table("authors").changes().run()

def main(dbname = 'test'):
    init_db()
    makeup_data()
    cursor = r.table("pages").run()
    for page in cursor:
        print page
    cursor = r.table("cells").run()
    for cell in cursor:
        print cell

if __name__ == '__main__':
    main()

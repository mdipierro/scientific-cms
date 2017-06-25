import rethinkdb as r

r.connect( "localhost", 28015).repl()
try:
    r.table_create("pages").run()
except:
    pass # page table already exists

def store(id, title, markup, code):
    res = r.table("pages").replace({'id': id, 'title': title, 'markup': markup, 'code': code}).run()
    if res['replaced'] == 0:
        r.table("pages").insert({'id': id, 'title': title, 'markup': markup, 'code': code}).run()

def retrieve(id):
    return r.table("pages").get(id).run()

def search(keywords):
    results = []
    pages = r.table("pages").run()
    for page in pages:
        print page['title'], keywords
        if all(keyword in page['title'] for keyword in keywords):
            results.append({'id':page['id'], 'title':page['title']})
    return results

if __name__ == '__main__':
    store(1,'test1','','')
    store(2,'test2','','')
    store(3,'test3','','')
    #print search(['test'])
    #print retrieve(1)
    pages = r.table("pages").run()
    for page in pages:
        print page

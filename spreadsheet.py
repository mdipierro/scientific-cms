import os, re, copy, json

class Spreadsheet(object):

    regex_string = re.compile('\w+')

    def __init__(self, name):
        self.name = name
        self.formulas = {}
        self.values = {}
        self.context = {}
        self.load(name)

    def load(self, name):
        if os.path.exists(name):
            with open(name) as myfile:
                self.formulas, self.values = json.load(myfile)

    def save(self, name):
        with open(name, 'w') as myfile:
            json.dump((self.formulas, self.values), myfile)

    def process(self, changes):
        keys = changes.keys()
        for key in changes:
            self.formulas[key] = changes[key]
        self.run()
        self.save(self.name)
        return {'formulas':self.formulas, 'values':self.values}

    def find_neighbors(self):
        neighbors = {key:[] for key in self.formulas}
        for k, value in self.formulas.iteritems():
            if isinstance(value, basestring) and value[:1] == '=':
                keys = self.regex_string.findall(value)
                [neighbors[i].append(k) for i in keys if i in neighbors]
        return neighbors

    def topological_sort(self, neighbors):
        sorted_keys, visited = [], set()
        def visit(k):
            if not k in visited:
                visited.add(k)
                [visit(i) for i in neighbors[k]]
                sorted_keys.insert(0, k)
        [visit(k) for k in self.formulas if k not in visited]
        return sorted_keys

    def run(self):
        values = copy.copy(self.context)
        neighbors = self.find_neighbors()
        sorted_keys = self.topological_sort(neighbors)
        for key in sorted_keys:
            value = self.formulas[key]
            if str(value).startswith('='):
                try:
                    value = eval(value[1:], {}, values) # NOT SAFE
                except Exception as e:
                    value = str(e)
            values[key] = value
        self.values = {key: values[key] for key in self.formulas}
            
def main():
    import math
    s = Spreadsheet('test')
    s.context = vars(math)
    changes = dict(x="=sin(c+a)", a=1, b=2, c='=a+d+e', d='=b-a', e='=a+b')
    print s.process(changes)
    changes = dict(a=2, x="=3*a")
    print s.process(changes)
    
if __name__ == '__main__': main()

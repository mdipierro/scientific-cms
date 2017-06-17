let app_init = () => {
    let app = {};
    let vue = app.vue = new Vue({
            el: '#target',
            data: {
                selected_key: null,
                selected_value: null,
                rows: [],
                cols: [],
                cells: {},
                values: {},
                to: {},
                from: {},
            },
            methods: {
                select: (key) => { app.select(key); }
            },
            watch: {
                selected_value: (value) => { app.selected_value(value); }
            }
        });
    app.select = (key) => {
        vue.selected_key = key;
        vue.selected_value = vue.cells[key];
        vue.$refs.input.focus();
    };
    app.selected_value = (value) => {
        let key = vue.selected_key;        
        let keys = value.match(/\w+/ig)||[];
        vue.cells[key] = vue.selected_value;
        keys = keys.filter((key) => { return key in vue.cells; });
        if(JSON.stringify(keys)!=JSON.stringify(JSON.stringify)) {
            let f = (i) => { return i!=key; };
            let g = (k) => { vue.from[k] = vue.from[k].filter(f); };
            vue.to[key].map(g);
            vue.to[key] = keys;
            keys.map((k)=>{ vue.from[k].push(key);});
        }  
        app.update(key)
    };
    app.update = (key) => {
        let old_value = vue.values[key];
        let value = vue.cells[key];
        if(old_value!=value) {
            if((''+value)[0]=='=') {
                try {
                    value = math.eval(value.substr(1), vue.values);
                    value = (typeof value == typeof {})?'obj':value;
                } catch(e) { value = 'error'; }
            }
            vue.values[key] = value;
            vue.from[key].map(app.update);
        }
    };
    app.init = () => {
        for(let i=1; i<=100; i++) {
            app.vue.rows.push(i);
            for(let j=1; j<=26; j++) {
                var c = String.fromCharCode(64+j);
                if(i==1) app.vue.cols.push(c);
                let key = c+i;
                app.vue.cells[key] = app.vue.values[key] = '';
                app.vue.to[key] = [];
                app.vue.from[key] = [];
            }
        }
    };
    app.init();
    return app;
};
    
let app = app_init();
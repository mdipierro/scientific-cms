let init_app = () => {
    let app = {};
    app.metamarked = (text) => {
        text = text.replace(/\[\[(\w+\:.*?)\]\]/g,(m)=>{
                let idx = m.indexOf(':');
                let name = m.substr(2,idx-2);
                let value = m.substr(idx+1,m.length-idx-3);
                app.vue.values[name] = value;
                app.vue.formulas[name] = value;
                if(['True','False'].indexOf(value)>=0) {
                    return '<input type="checkbox" id="input-'+name+'" value="'+value+'"/>';
                } else {
                    return '<input id="input-'+name+'" value="'+value+'"/>';
                }
            });
        text = text.replace(/\[\[(\w+\=.*?)\]\]/g, (m)=>{
                let idx = m.indexOf('=');
                let name = m.substr(2,idx-2);
                let formula = m.substr(idx,m.length-idx-2);
                app.vue.formulas[name] = formula;
                return '<span id="output-'+name+'" >'+formula+'</span>';
            });
        text =  marked(text);
        return text;
    };
    app.process = () => {
        let data = {'values':app.vue.values, 'formulas':app.vue.formulas};
        axios.post('/compute',data).then(app.handle_response);
    };
    app.command_page = (data) => {
        app.vue.title = data.page.title;
        app.vue.markup = data.page.markup;
        app.vue.code = data.page.code;
        Vue.nextTick(app.send_formulas);
    };
    app.command_values = (data) => {
        for(let key in data.values) {            
            if(data.values[key][0]=='<')
                jQuery('#output-'+key).html(data.values[key]);
            else
                jQuery('#output-'+key).text(data.values[key]);
        }
    };
    app.command_search_results = (data) => {
        app.vue.search_results = data.items;
    };
    app.handle_response = (data) => {
        data = JSON.parse(data);
        if(data.command == 'page' && data.page.id == app.vue.id) app.command_page(data);
        else if(data.command == 'values') app.command_values(data);
        else if(data.command == 'search-results') app.command_search_results(data);
    };
    app.onkeyup = (event) => {
        let value = jQuery(event.target).val();
        let name = event.target.id.substr(6);
        app.vue.values[name] = value;
        app.vue.formulas[name] = value;
        app.send_formulas();
    };
    app.reconnected = () => {
        let data = {'command':'open', 'id':app.vue.id};
        app.ws.send(JSON.stringify(data));
    };   
    app.save = () => {
        let page = {'id':app.vue.id, 'title':app.vue.title, 'markup':app.vue.markup, 'code':app.vue.code};
        let data = {'command':'save', 'page':page};
        app.ws.send(JSON.stringify(data));
    };
    app.send_formulas = () => {
        data = {'command':'compute', 'id':app.vue.id, 'formulas':app.vue.formulas, 'code':app.vue.code};
        app.ws.send(JSON.stringify(data));
    };
    app.init = () => {
        app.vue.id = window.location.hash.substr(1);
        app.domain = window.location.href.split('/')[2];
        app.ws = new ReconnectingWebSocket('ws://'+app.domain+'/websocket');
        app.ws.onopen = app.reconnected;
        app.ws.onmessage = (evt) => { app.handle_response(evt.data); };
        jQuery('.output').on('keyup','input',app.onkeyup);
        jQuery(window).on('hashchange', () => { app.vue.id=window.location.hash.substr(1); app.reconnected(); });
    };
    app.search = () => {
        app.ws.send(JSON.stringify({'command':'search', 'keywords':app.vue.keywords}));
    };
    app.data = {
        id: 'test1',
        title: '',
        markup: '',
        code: '',
        formulas: {},
        values: {},
        keywords: '',
        search_results: []
    };
    app.methods = {
        metamarked: app.metamarked,
        save: app.save        
    };
    app.filters = {
    };
    app.watch = {
        markup: app.send_formulas,
        code: app.send_formulas,
        keywords: app.search,
        id: app.reconnect
    };
    app.vue = new Vue({el: '#target', data: app.data, methods: app.methods, filters: app.filters, watch: app.watch});
    app.init();
    return app;
};
    
let app = init_app();
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
    app.data = {
        input: '',
        code: '',
        formulas: {},
        values: {}
    };
    app.methods = {
        metamarked: app.metamarked
    };
    app.filters = {
    };
    app.watch = {
        input: () => {app.send_data();},
        code: () => {app.send_data();},
    };
    app.vue = new Vue({el: '#target', data: app.data, methods: app.methods, filters: app.filters, watch: app.watch});
    app.process = () => {
        let data = {'values':app.vue.values, 'formulas':app.vue.formulas};
        axios.post('/compute',data).then(app.handle_response);
    };
    app.handle_response = (data) => {
        data = JSON.parse(data);
        for(let key in data.values) {            
            if(data.values[key][0]=='<')
                jQuery('#output-'+key).html(data.values[key]);
            else
                jQuery('#output-'+key).text(data.values[key]);
        }
    };
    app.onkeyup = (event) => {
        console.log('keyup');
        let value = jQuery(event.target).val();
        let name = event.target.id.substr(6);
        app.vue.values[name] = value;
        app.vue.formulas[name] = value;
        app.send_data();
    };
    app.send_data = () => {
        data = {'formulas':app.vue.formulas, 'code':app.vue.code};
        app.ws.send(JSON.stringify(data));
    };
    
    app.init = () => {
        app.domain = window.location.href.split('/')[2];
        app.ws = new ReconnectingWebSocket('ws://'+app.domain+'/websocket/test1');
        app.ws.onopen = () => {};
        app.ws.onmessage = (evt) => { app.handle_response(evt.data); };
        jQuery('.output').on('keyup','input',app.onkeyup);
    };
    app.init();
    return app;
};
    
let app = init_app();
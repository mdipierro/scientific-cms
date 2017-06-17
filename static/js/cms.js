let init_app = () => {
    let app = {};
    app.metamarked = (text) => {
        text = text.replace(/\[\[(\w+)\]\]/g,(m)=>{
                return '<input id="input-'+m.substr(2,m.length-4)+'"/>';
            });
        text = text.replace(/\[\[(\w+\=.*?)\]\]/g,(m)=>{
                let idx = m.indexOf('=');
                let name = m.substr(2,idx-2);
                let formula = m.substr(idx,m.length-2);
                app.vue.formulas[name] = formula;
                return '<div id="output-'+name+'" >(output)</div>';
            });
        text =  marked(text);
        return text;
    };
    app.data = {
        input: '',
        code: '',
        vars: {},
        formulas: {}
    };
    app.methods = {
        metamarked: app.metamarked
    };
    app.filters = {
    };
    app.watch = {
    };
    app.vue = new Vue({el: '#target', data: app.data, methods: app.methods, filters: app.filters, watch: app.watch});
    app.onkeyup = (event) => {
        console.log('keyup');
        let value = jQuery(event.target).val();
        let name = event.target.id.substr(6);
        app.vue.vars[name] = value;

        for(let key in app.vue.vars) {
            if(app.vue.vars[key][0]==':')
                jQuery('#output-'+key).html(app.vue.vars[key]);
            else
                jQuery('#output-'+key).text(app.vue.vars[key]);
        }
    };
    jQuery('.output').on('keyup','input',app.onkeyup);
    return app;
};
    
let app = init_app();
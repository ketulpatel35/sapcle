odoo.define('emp_self_services.CalendarModel', function (require) {
"use strict";

var CalendarModel = require('web.CalendarModel');
var core = require('web.core');
var fieldUtils = require('web.field_utils');
var session = require('web.session');

var _t = core._t;

return CalendarModel.include({
    _loadFilter: function (filter) {
        if (!filter.write_model) {
            return;
        }
        var field = this.fields[filter.fieldName];
        return this._rpc({
                model: filter.write_model,
                method: 'search_read',
                domain: [["user_id", "=", session.uid]],
                fields: [filter.write_field],
            })
            .then(function (res) {
                var records = _.map(res, function (record) {
                    var _value = record[filter.write_field];
                    var value = _.isArray(_value) ? _value[0] : _value;
                    var f = _.find(filter.filters, function (f) {return f.value === value;});
                    var formater = fieldUtils.format[_.contains(['many2many', 'one2many'], field.type) ? 'many2one' : field.type];
                    return {
                        'id': record.id,
                        'value': value,
                        'label': formater(_value, field),
                        'active': !f || f.active,
                    };
                });
                records.sort(function (f1,f2) {
                    return _.string.naturalCmp(f2.label, f1.label);
                });
            });
    },
});

});
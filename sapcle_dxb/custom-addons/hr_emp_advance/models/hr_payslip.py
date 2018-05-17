from odoo import fields, models, api, _
# from datetime import datetime
# from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DATEFORMAT
from odoo.exceptions import ValidationError


class HRPayslip(models.Model):
    _inherit = 'hr.payslip'

    employee_advance_ids = fields.One2many(
        'hr.payslip.employee.advance', 'payslip_id', 'Advance')

    @api.multi
    def get_employee_advance_lines(self, employee_id, date_from, date_to):
        """
        get employee advance
        :param employee_id:
        :param date_from:
        :param date_to:
        :return:
        """
        employee_advance_rec = self.env['employee.advance'].search([
            ('employee_id','=', employee_id),
            ('is_payslip_generated', '!=', True),
            ('effective_date', '>=', date_from),
            ('effective_date', '<=', date_to),
            ('state', '=', 'done')])
        return employee_advance_rec

    @api.multi
    def onchange_employee_id(self, date_from, date_to, employee_id=False, contract_id=False):
        """
        :param date_from:
        :param date_to:
        :param employee_id:
        :param contract_id:
        :return:
        """
        res = super(HRPayslip, self).onchange_employee_id(
            date_from, date_to, employee_id, contract_id)
        employee_advance_rec = self.get_employee_advance_lines(
            employee_id, date_from, date_to)
        emp_advance_list2 = [{
            'name': y.name,
            'employee_id': y.employee_id.id,
            'date': y.effective_date,
            'amount': y.amount,
            'code': y.code,
            'currency_id': y.currency_id.id,
            'employee_advance_id': y.id,
        } for y in employee_advance_rec]
        res['value'].update({'employee_advance_ids': emp_advance_list2})
        return res

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):
        """
        employee onchange
        :return:
        """
        res = super(HRPayslip, self).onchange_employee()
        employee_advance_rec = self.get_employee_advance_lines(
            self.employee_id.id, self.date_from, self.date_to)
        emp_advance_list1 = [(2, x,) for x in self.employee_advance_ids.ids]
        emp_advance_list2 = [(0,0,{
            'name': y.name,
            'employee_id': y.employee_id.id,
            'date': y.effective_date,
            'amount': y.amount,
            'code': y.code,
            'currency_id': y.currency_id.id,
            'employee_advance_id': y.id,
        }) for y in employee_advance_rec]
        emp_advance_list = emp_advance_list1 + emp_advance_list2
        self.employee_advance_ids = emp_advance_list
        return res

    @api.multi
    def action_payslip_done(self):
        for rec in self.employee_advance_ids:
            rec.employee_advance_id.write({'is_payslip_generated': True})
        res = super(HRPayslip, self).action_payslip_done()
        return res


class HRPayslipEmployeeAdvance(models.Model):
    _name = 'hr.payslip.employee.advance'

    name = fields.Char('Description')
    payslip_id = fields.Many2one('hr.payslip', 'Payslip')
    employee_id = fields.Many2one('hr.employee', "Employee")
    date = fields.Date('Date')
    amount = fields.Float('Amount')
    code = fields.Char('Code')
    currency_id = fields.Many2one('res.currency', 'Currency')
    employee_advance_id = fields.Many2one('employee.advance',
                                          'Employee Advance')


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    @api.multi
    def compute_sheet(self):
        payslips = self.env['hr.payslip']
        [data] = self.read()
        active_id = self.env.context.get('active_id')
        if active_id:
            [run_data] = self.env['hr.payslip.run'].browse(active_id).read(
                ['date_start', 'date_end', 'credit_note'])
        from_date = run_data.get('date_start')
        to_date = run_data.get('date_end')
        if not data['employee_ids']:
            raise ValidationError(_("You must select employee(s) to "
                                    "generate payslip(s)."))
        for employee in self.env['hr.employee'].browse(data['employee_ids']):
            slip_data = self.env['hr.payslip'].onchange_employee_id(
                from_date, to_date, employee.id, contract_id=False)
            res = {
                'employee_id': employee.id,
                'name': slip_data['value'].get('name'),
                'struct_id': slip_data['value'].get('struct_id'),
                'contract_id': slip_data['value'].get('contract_id'),
                'payslip_run_id': active_id,
                'input_line_ids': [(0, 0, x) for x in slip_data['value'].get(
                    'input_line_ids')],
                'worked_days_line_ids': [(0, 0, x) for x in slip_data[
                    'value'].get('worked_days_line_ids')],
                'employee_advance_ids': [(0, 0, x) for x in slip_data[
                    'value'].get('employee_advance_ids')],
                'date_from': from_date,
                'date_to': to_date,
                'credit_note': run_data.get('credit_note'),
            }
            payslips += self.env['hr.payslip'].create(res)
        payslips.compute_sheet()
        return {'type': 'ir.actions.act_window_close'}

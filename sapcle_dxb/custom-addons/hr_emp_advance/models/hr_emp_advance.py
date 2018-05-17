from odoo import fields, models, api, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DATEFORMAT
from odoo.exceptions import ValidationError


class EmployeeAdvance(models.Model):
    _name = 'employee.advance'
    _inherit = ['mail.thread']
    _description = 'Employee Advance'
    _order = 'name desc'

    name = fields.Char('Description')
    employee_id = fields.Many2one(
        'hr.employee', "Employee",
        default=lambda self: self.env['hr.employee'].search(
            [('user_id', '=', self.env.user.id)], limit=1))
    date = fields.Date('Requested date', default=datetime.today().date())
    effective_date = fields.Date('Allocation Date')
    amount = fields.Float('Amount')
    salary_rule_id = fields.Many2one(
        'hr.salary.rule', string='Type', required=True)
    code = fields.Char('Code', related='salary_rule_id.code')
    state = fields.Selection([('draft', 'Draft'),
                              ('manager_approval', 'Submitted'),
                              ('approved', 'Verified'),
                              ('done', 'Paid'), ('canceled', 'Canceled')],
                             default='draft')
    currency_id = fields.Many2one(
        'res.currency', 'Currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id.id)
    is_payslip_generated = fields.Boolean('Payslip Generated', )
    refuse_reason = fields.Text('Refuse Reason')
    note_ids = fields.One2many('employee.advance.note',
                               'employee_advance_id', 'Notes')
    # payslip_id = fields.Many2one('hr.payslip', 'Payslip')

    @api.multi
    def submit_to_manager(self):
        """
        :return:
        """
        for rec in self:
            rec.state = 'manager_approval'

    @api.multi
    def set_to_draft(self):
        """
        :return:
        """
        for rec in self:
            rec.state = 'draft'

    @api.multi
    def manager_approved(self):
        """
        :return:
        """
        for rec in self:
            rec.state = 'approved'

    @api.multi
    def manager_paid_amount(self):
        """
        :return:
        """
        for rec in self:
            rec.state = 'done'

    @api.multi
    def manager_canceled(self):
        """
        :return:
        """
        for rec in self:
            rec.state = 'canceled'

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_('you can not delete record, which is '
                                        'not in draft!'))
        return super(EmployeeAdvance, self).unlink()


class EmployeeAdvanceNote(models.Model):
    _name = 'employee.advance.note'

    employee_id = fields.Many2one(
        'hr.employee', "Note By",
        default=lambda self: self.env['hr.employee'].search(
            [('user_id', '=', self.env.user.id)], limit=1))
    note = fields.Text('Description')
    employee_advance_id = fields.Many2one(
        'employee.advance', 'Employee Advance')

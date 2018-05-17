from odoo import fields, models, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError
from datetime import date, datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DATEFORMAT


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    state = fields.Selection(
        [('draft', 'Draft'), ('submit', 'Submitted'), ('approve', 'Verified'),
         ('post', 'Posted'), ('done', 'Paid'), ('cancel', 'Refused')],
        string='Status', index=True, readonly=True,
        track_visibility='onchange', copy=False, default='draft',
        required=True, help='Expense Report State')

    expense_line_ids = fields.One2many(
        'hr.expense', 'sheet_id', string='Expense Lines', readonly=False,
        copy=False)
    refuse_reason = fields.Text('Refuse Reason')
    note_ids = fields.One2many('expense.sheet.note', 'hr_expense_sheet_id',
                               'Notes')

    @api.multi
    def action_open_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id(
            'base', 'action_attachment')
        res['domain'] = [('res_model', '=', 'hr.expense.sheet'),
                         ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'hr.expense.sheet',
                          'default_res_id': self.id}
        return res

    @api.multi
    def action_submit_for_manager_approval(self):
        """
        :return:
        """
        for rec in self:
            if not rec.expense_line_ids:
                raise ValidationError(_('Add Expanse Line !'))
            to_day = date.today()
            for line_rec in rec.expense_line_ids:
                c_date = datetime.strptime(line_rec.date, OE_DATEFORMAT).date()
                if c_date > to_day:
                    raise ValidationError(_(
                        'you can not apply expanse request with future date '
                        '%s.')%(line_rec.date))
            existing_attachement = self.env['ir.attachment'].search([
                ('res_id', '=', rec.id), ('res_model', '=', rec._name)])
            if not existing_attachement:
                raise ValidationError(
                    _('You are not allowed to submit the request without'
                      'attaching a document.\n For attaching a document:'
                      'press save then attach a document.'))
            rec.state = 'submit'

    @api.multi
    def approved_expense_posted(self):
        """
        :return:
        """
        for rec in self:
            rec.state = 'post'

    # @api.model
    # def default_get(self, fields_list):
    #     res = super(HrExpenseSheet, self).default_get(fields_list)
    #     if self.env.uid:
    #         employee_rec = self.env['hr.employee'].search([
    #             ('user_id', '=', self.env.uid)], limit=1)
    #         if employee_rec:
    #             res.update({'employee_id': employee_rec.id})
    #     return res

class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense'

    name = fields.Char(string='Expense Description', required=True,
                       readonly=False)
    date = fields.Date(default=fields.Date.context_today, readonly=False,
                       string="Expense Date")
    product_id = fields.Many2one('product.product', string='Expense Type',
                                 required=True, readonly=False)
    unit_amount = fields.Float(string='Unit Price', required=True,
                               readonly=False,
                               digits=dp.get_precision('Product Price'))

    state = fields.Selection([
        ('draft', 'To Submit'),
        ('reported', 'Reported'),
        ('done', 'Posted'),
        ('refused', 'Refused')
        ], compute='_compute_state', string='Status', copy=False,
        index=True, readonly=True, store=True, help="Status of the expense.")

    @api.depends('sheet_id', 'sheet_id.account_move_id', 'sheet_id.state')
    def _compute_state(self):
        for expense in self:
            if not expense.sheet_id:
                expense.state = "draft"
            elif expense.sheet_id.state == "draft":
                expense.state = "draft"
            elif expense.sheet_id.state == "cancel":
                expense.state = "refused"
            elif not expense.sheet_id.account_move_id:
                expense.state = "reported"
            else:
                expense.state = "done"


class ExpenseSheet(models.Model):
    _name = 'expense.sheet.note'

    employee_id = fields.Many2one(
        'hr.employee', "Note By",
        default=lambda self: self.env['hr.employee'].search(
            [('user_id', '=', self.env.user.id)], limit=1))
    note = fields.Text('Description')
    hr_expense_sheet_id = fields.Many2one(
        'hr.expense.sheet', 'Employee Advance')

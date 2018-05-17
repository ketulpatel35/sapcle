from odoo import models, fields, api, _


class HrExpenseRefuse(models.TransientModel):
    _name = 'expense.refuse.wiz'
    _description = 'Expense Refuse'

    reason = fields.Text(string='Reason/Justification', required=1)

    @api.multi
    def button_confirm(self):
        """
        :return:
        """
        if self._context.get('active_id'):
            active_id = self._context.get('active_id')
            active_rec = self.env['hr.expense.sheet'].browse(active_id)
        for rec in active_rec:
            reason = self.env.user.name + ': ' + self.reason + '\n'
            if rec.state == 'submit':
                if rec.refuse_reason:
                    reason = rec.refuse_reason + reason
                rec.refuse_reason = reason
                rec.state = 'draft'
            if rec.state == 'approve':
                if rec.refuse_reason:
                    reason = rec.refuse_reason + reason
                rec.refuse_reason = reason
                rec.state = 'submit'

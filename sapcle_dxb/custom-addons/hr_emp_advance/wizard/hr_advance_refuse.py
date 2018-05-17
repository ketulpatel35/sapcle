from odoo import models, fields, api, _


class HrAdvanceRefuse(models.TransientModel):
    _name = 'advance.refuse.wiz'
    _description = 'Advance Refuse'

    reason = fields.Text(string='Reason/Justification', required=1)

    @api.multi
    def button_confirm(self):
        """
        :return:
        """
        if self._context.get('active_id'):
            active_id = self._context.get('active_id')
            active_rec = self.env['employee.advance'].browse(active_id)
        for rec in active_rec:
            reason = self.env.user.name + ': ' + self.reason + '\n'
            if rec.state == 'manager_approval':
                if rec.refuse_reason:
                    reason = rec.refuse_reason + reason
                rec.refuse_reason = reason
                rec.state = 'draft'
            if rec.state == 'approved':
                if rec.refuse_reason:
                    reason = rec.refuse_reason + reason
                rec.refuse_reason = reason
                rec.state = 'manager_approval'

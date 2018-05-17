from odoo import api, fields, models, _
from odoo.exceptions import Warning


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.res_model == 'hr.expense.sheet' and rec.res_id:
                expense_rec = self.env['hr.expense.sheet'].browse(rec.res_id)
                if expense_rec and expense_rec.state not in ['draft']:
                    raise Warning(_('You can not delete Expense attachment!'))
        return super(IrAttachment, self).unlink()

from odoo import api, fields, models, _
from odoo.exceptions import Warning


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.res_model == 'employee.advance' and rec.res_id:
                advance_rec = self.env['employee.advance'].browse(rec.res_id)
                if advance_rec and advance_rec.state in ['approved', 'done']:
                    raise Warning(_('You can not delete Advance attachment!'))
        return super(IrAttachment, self).unlink()
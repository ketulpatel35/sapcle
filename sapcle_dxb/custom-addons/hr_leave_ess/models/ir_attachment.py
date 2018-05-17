from odoo import api, fields, models, _
from odoo.exceptions import Warning


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.res_model == 'hr.holidays' and rec.res_id:
                leave_record = self.env['hr.holidays'].browse(rec.res_id)
                if leave_record and leave_record.state != 'draft':
                    raise Warning(_('You can not delete Leave attachment!'))
        return super(IrAttachment, self).unlink()
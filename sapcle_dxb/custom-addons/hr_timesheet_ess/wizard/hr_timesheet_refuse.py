from odoo import models, fields, api, _


class HrTimesheetRefuse(models.TransientModel):
    _name = 'timesheet.refuse.wiz'
    _description = 'Timesheet Refuse'

    reason = fields.Text(string='Reason/Justification', required=1)

    @api.multi
    def button_confirm(self):
        """
        :return:
        """
        if self._context.get('active_id'):
            active_id = self._context.get('active_id')
            active_rec = self.env['timesheet.checklist'].browse(active_id)
        for rec in active_rec:
            if rec.state == 'manager_approval':
                rec.state = 'draft'
            if rec.state == 'hr_approval':
                rec.state = 'manager_approval'

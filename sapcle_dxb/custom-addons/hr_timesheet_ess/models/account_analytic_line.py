from odoo import fields, models, api, _
from datetime import datetime
import calendar
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DATEFORMAT


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    _order = 'date'

    @api.depends('date')
    def _get_day(self):
        for rec in self:
            date = datetime.strptime(rec.date, OE_DATEFORMAT)
            rec.week_day = calendar.day_name[date.weekday()]

    timesheet_checklist_id = fields.Many2one(
        'timesheet.checklist', 'Timesheet Checklist')
    ts_status = fields.Selection([
        ('fd', 'Full Day'), ('hd', 'Half Day'), ('wo', 'Week Off'),
        ('l', 'Leave'), ('ph', 'Public Holiday')], string="Attendance")
    week_day = fields.Char(string="Day", compute='_get_day', store=True)

    @api.onchange('ts_status')
    def onchange_status(self):
        for rec in self:
            if rec.ts_status == 'fd':
                rec.unit_amount = 8.00
            elif rec.ts_status == 'hd':
                rec.unit_amount = 4.00
            elif rec.ts_status == 'wo':
                rec.unit_amount = 0.00
            elif rec.ts_status == 'l':
                rec.unit_amount = 0.00
            elif rec.ts_status == 'ph':
                rec.unit_amount = 8.00
            else:
                rec.unit_amount = 0.00
from odoo import models, api, fields, _


class HrHolidaysStatus(models.Model):
    _inherit = 'hr.holidays.status'

    attachment_mandatory = fields.Boolean('Attachment is mandatory')
    eligible_months = fields.Integer('Eligible After')
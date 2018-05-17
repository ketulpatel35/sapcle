from odoo import fields, models, api, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DATEFORMAT


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def _compute_attached_documents(self):
        for employee_rec in self:
            employee_rec.document_count = \
                self.env['employee.documents'].search_count([
                    ('employee_id', '=', employee_rec.id)])

    joining_date = fields.Date('Joining Date')
    document_count = fields.Integer(compute='_compute_attached_documents',
                                    string="Number of documents attached")
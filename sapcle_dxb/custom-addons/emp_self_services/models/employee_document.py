from odoo import models, fields, api,_
from datetime import date
from odoo.exceptions import Warning, ValidationError

class EmployeeDocuments(models.Model):
    _name = 'employee.documents'

    name = fields.Char('Documents Name')
    employee_id = fields.Many2one(
        'hr.employee', string='Employee Name', track_visibility='onchange')
    document_type = fields.Selection([('file', 'File')], default='file')
    file_name = fields.Char()
    file_content = fields.Binary(string='File')
    date_upload = fields.Date('Date Uploaded', default=date.today())
    uploaded_by = fields.Many2one('res.users', 'Uploaded By',
                                  default=lambda self: self.env.user.id,
                                  track_visibility='onchange')
    url = fields.Char('Url')
    remarks = fields.Text('Remarks')

    @api.multi
    def unlink(self):
        for data in self:
            raise ValidationError(
                _('You are not allowed to delete a record'))
        return super(EmployeeDocuments, self).unlink()

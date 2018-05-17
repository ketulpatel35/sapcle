from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
import math


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    state = fields.Selection([
        ('draft', 'To Submit'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved'), ('cancel', 'Cancelled')],
        string='Status', readonly=True, track_visibility='onchange',
        copy=False, default='draft')

    start_day_status = fields.Selection([('full', 'Full'), ('half', 'Half')],
                                 default='full')
    end_day_status = fields.Selection([('full', 'Full'), ('half', 'Half')],
                                 default='full')

    @api.model
    def compute_number_of_months(self, f_date, e_date):
        """
        :return:
        """
        delta = e_date.date() - f_date
        return delta.days / 12

    @api.multi
    def action_confirm(self):
        for rec in self:
            if rec.holiday_status_id.attachment_mandatory:
                ir_obj = self.env['ir.attachment']
                existing_attachement = ir_obj.search([
                    ('res_id', '=', rec.id),
                    ('res_model', '=', rec._name)])
                if not existing_attachement:
                    raise ValidationError(
                        _('You are not allowed to submit the request without '
                          'attaching a document.\n For attaching a document: '
                          'press save then attach a document.'))
            if rec.holiday_status_id.eligible_months > 0:
                joining_date = rec.employee_id.joining_date or False
                if not joining_date:
                    raise ValidationError(_('Joining date not set for this '
                                            'employee.!'))
                j_date = datetime.strptime(joining_date,
                                           DEFAULT_SERVER_DATE_FORMAT).date()
                s_date = datetime.strptime(rec.date_from,
                                           DEFAULT_SERVER_DATETIME_FORMAT)
                get_month = self.compute_number_of_months(
                    j_date, s_date)
                if rec.holiday_status_id.eligible_months > get_month:
                    raise ValidationError(_(
                        'You are not Eligible to Apply This Leave Before %s '
                        'Months!')%(rec.holiday_status_id.eligible_months))
        return super(HrHolidays, self).action_confirm()

    @api.onchange('date_from')
    def _onchange_date_from(self):
        """
        :return:
        """
        if self.date_from:
            self.date_from = self.date_from.split(' ')[0] + ' 00:00:00'
            if self._context.get('update_status'):
                self.start_day_status = 'full'
                self.end_day_status = 'full'
        res = super(HrHolidays, self)._onchange_date_from()
        return res

    @api.onchange('date_to')
    def _onchange_date_to(self):
        """ Update the number_of_days. """
        if self.date_to:
            self.date_to = self.date_to.split(' ')[0] + ' 19:59:59'
            if self._context.get('update_status'):
                self.start_day_status = 'full'
                self.end_day_status = 'full'
        res = super(HrHolidays, self)._onchange_date_from()
        return res

    @api.onchange('start_day_status')
    def onchange_start_day_status(self):
        """
        :return:
        """
        if self.date_from:
            self._onchange_date_to()
            if self.start_day_status == 'half':
                if self.number_of_days_temp:
                    self.number_of_days_temp -= 0.5
            if self.end_day_status == 'half':
                if self.number_of_days_temp:
                    self.number_of_days_temp -= 0.5

    @api.onchange('end_day_status')
    def onchange_end_day_status(self):
        """
        :return:
        """
        self.onchange_start_day_status()
        # if self.date_to:
        #     self._onchange_date_to()
        #     if self.end_day_status == 'half':
        #         if self.number_of_days_temp:
        #             self.number_of_days_temp -= 0.5
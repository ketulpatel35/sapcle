from odoo import fields, models, api, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DATEFORMAT
# from odoo.exceptions import ValidationError
# from dateutil import rrule, parser

class HRPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.depends('date_from', 'date_to')
    def compute_number_of_days(self):
        """
        :return:
        """
        for rec in self:
            if rec.date_from and rec.date_to:
                f_date = datetime.strptime(rec.date_from, OE_DATEFORMAT)
                e_date = datetime.strptime(rec.date_to, OE_DATEFORMAT)
            delta = e_date - f_date
            rec.number_of_days = delta.days + 1


    number_of_days = fields.Integer('Number Of Days',
                                    compute='compute_number_of_days')

    @api.model
    def get_worked_day_lines_from_timesheets(self, contracts, date_from,
                                             date_to):
        """
        :param contracts:
        :param date_from:
        :param date_to:
        :return:
        """
        worked_day_lines = []
        for contract in contracts.filtered(
                lambda contract: contract.resource_calendar_id):
            line_data = {'number_of_hours': 0.0,
                         'sequence': 2,
                         'contract_id': contract.id,
                         'number_of_days': 0.0,
                         'name': 'Timesheet Working Days paid at 100%',
                         'code': 'WORK1001'}
            number_of_days = 0.0
            number_of_hours = 0.0
            for timesheet_line in self.env['account.analytic.line'].search([
                ('date', '>=', date_from), ('date', '<=', date_to),
                ('employee_id', '=', contract.employee_id.id)
            ]):
                if timesheet_line.timesheet_checklist_id and \
                        timesheet_line.timesheet_checklist_id.state in [
                            'hr_approval', 'approved']:
                    if timesheet_line.ts_status == 'fd':
                        number_of_days += 1
                    elif timesheet_line.ts_status == 'hd':
                        number_of_days += 0.5
                    number_of_hours += timesheet_line.unit_amount
            line_data['number_of_hours'] = number_of_hours
            line_data['number_of_days'] = number_of_days
            if number_of_days != 0.0:
                worked_day_lines.append(line_data)
        return worked_day_lines

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        """
        @param contract: Browse record of contracts
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        line1 = super(HRPayslip, self).get_worked_day_lines(
            contracts, date_from, date_to)
        line2 = self.get_worked_day_lines_from_timesheets(
            contracts, date_from, date_to)
        if not line1:
            line1 = []
        if not line2:
            line2 = []
        res = line1 + line2
        return res

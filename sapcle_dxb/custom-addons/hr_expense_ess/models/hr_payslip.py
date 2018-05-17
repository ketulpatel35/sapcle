from odoo import fields, models, api, _
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DATEFORMAT
# from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DATEFORMAT
# from odoo.exceptions import ValidationError
# from dateutil import rrule, parser


class HRPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def get_expanse_input(self, contracts, date_from, date_to):
        """
        :param contracts:
        :param date_from:
        :param date_to:
        :return:
        """
        res = []
        for contract in contracts:
            code_data = {}
            for sheet_rec in self.env['hr.expense.sheet'].search([
                ('employee_id', '=', contract.employee_id.id),
                ('state', '=', 'post')]):
                for exp_rec in sheet_rec.expense_line_ids:
                    start = datetime.strptime(date_from, OE_DATEFORMAT)
                    end = datetime.strptime(date_to, OE_DATEFORMAT)
                    date = datetime.strptime(exp_rec.date, OE_DATEFORMAT)
                    if start <= date <= end:
                        if exp_rec.product_id and \
                                exp_rec.product_id.default_code:
                            if exp_rec.product_id.default_code not in \
                                    code_data:
                                code_data.update({
                                    exp_rec.product_id.default_code:
                                        exp_rec.total_amount})
                            else:
                                amount = code_data.get(
                                    exp_rec.product_id.default_code) + \
                                         exp_rec.total_amount
                                code_data.update({
                                    exp_rec.product_id.default_code:amount})
            for k_data, v_data in code_data.items():
                input_data = {
                    'name': 'Expense Reimbursements - Earnings',
                    'code': k_data,
                    'contract_id': contract.id,
                    'amount': v_data,
                }
                res += [input_data]
        return res

    @api.model
    def get_inputs(self, contracts, date_from, date_to):
        res = super(HRPayslip, self).get_inputs(contracts, date_from, date_to)
        for el in res:
            if el['name'] == 'Expense Reimbursements - Earnings':
                res.remove(el)
        exp_data = self.get_expanse_input(contracts, date_from, date_to)
        if exp_data:
            res += exp_data
        return res
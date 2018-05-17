from odoo import fields, models, api, _


class HRPayslip(models.Model):
    _inherit = 'hr.payslip'

    state = fields.Selection([
        ('draft', 'Draft'), ('verify', 'Waiting'), ('done', 'Confirm'),
        ('paid', 'Paid'), ('cancel', 'Rejected')], string='Status',
        index=True, readonly=True, copy=False, default='draft',
        help="""* When the payslip is created the status is \'Draft\
        \n* If the payslip is under verification, the status is \'Waiting\'.
        \n* If the payslip is confirmed then status is set to \'Done\'.
        \n* When user cancel payslip the status is \'Rejected\'.""")

    @api.multi
    def action_payslip_paid(self):
        """
        paid payslip
        :return:
        """
        for rec in self:
            rec.state = 'paid'

    @api.multi
    def compute_sheet(self):
        for payslip in self:
            number = payslip.number or self.env['ir.sequence'].next_by_code(
                'salary.payslip')
            # delete old payslip lines
            payslip.line_ids.unlink()
            # set the list of contract for which the rules have to be applied
            # if we don't give the contract, then the rules to apply should be for all current contracts of the employee
            contract_ids = payslip.contract_id.ids or \
                self.get_contract(payslip.employee_id, payslip.date_from, payslip.date_to)
            lines = [(0, 0, line) for line in self._get_payslip_lines(contract_ids, payslip.id)]
            payslip.write({'line_ids': lines, 'number': number})
        return True

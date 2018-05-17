# -*- coding: utf-8 -*-
##############################################################################
# Ketul & Lithin
##############################################################################

from odoo import models, fields, api, _
from odoo.http import request
import datetime


class HrDashboard(models.Model):
    _name = 'hr.dashboard'
    _description = 'HR Dashboard'

    name = fields.Char("")

    @api.model
    def _check_group(self, group_xml_id_lst):
        user_rec = self.env.user
        for group_xml_id in group_xml_id_lst:
            if user_rec.has_group(str(group_xml_id)):
                return True
        return False

    @api.model
    def get_employee_info(self):
        """
        The function which is called from hr_dashboard.js.
        To fetch enough data from model hr and related dependencies.
        :payroll_dataset Total payroll generated according to months from model hr_payslip and hr_payslip_lines.
        :attendance_data Total worked hours and attendance details from models hr_attendace and hr_employee.
        :employee_table dict of datas from models hr_employee, hr_job, hr_department.
        :rtype dict
        :return: data
        """
        uid = request.session.uid
        cr = self.env.cr
        employee_id = self.env['hr.employee'].sudo().search_read([
            ('user_id', '=', uid)], limit=1)
        if not employee_id:
            raise Warning(_('Kindly, contact the HR team to link your user '
                            'with an employee profile.'))
        leave_search_view_id = self.env.ref(
            'hr_holidays.view_hr_holidays_filter')
        leave_summary_view_id = self.env.ref('hr_holidays.view_holiday_simple')
        leaves_to_approve = self.env['hr.holidays'].sudo().search_count([
            ('state', 'in', ['confirm', 'validate1']),
            ('type', '=', 'remove')])
        leaves_alloc_to_approve = self.env[
            'hr.holidays'].sudo().search_count([
            ('state', 'in', ['confirm', 'validate1']), ('type', '=', 'add')])
        is_leave_manager = self._check_group([
            'hr_holidays.group_hr_holidays_manager'])
        timesheet_search_view_id = self.env.ref(
            'hr_timesheet.hr_timesheet_line_search')
        job_search_view_id = self.env.ref(
            'hr_recruitment.view_crm_case_jobs_filter')
        is_timesheet_verify = self._check_group(
            ['hr_timesheet.group_hr_timesheet_user'])
        is_timesheet_approve = self._check_group(
            ['hr_timesheet.group_timesheet_manager'])
        # Expense
        expense_search_view_id = self.env.ref(
            'hr_expense.view_hr_expense_sheet_filter')
        is_expense_manager = self._check_group(
            ['hr_expense.group_hr_expense_manager'])
        is_expense_finance = self._check_group([
            'hr_expense_ess.group_finance_expense_manager'])
        expenses_to_approve = self.env[
            'hr.expense.sheet'].sudo().search_count([
            ('state', 'in', ['submit'])])
        expense_to_pay = self.env[
            'hr.expense.sheet'].sudo().search_count([
            ('state', 'in', ['approve'])])
        is_advance_manager = self._check_group([
            'hr_emp_advance.group_employee_advance_manager'])
        advance_to_approve = self.env['employee.advance'].sudo().search_count(
            [('state','in',['manager_approval', 'approved'])])
        is_advance_finance = self._check_group([
            'hr_emp_advance.group_employee_finance_manager'])
        advance_to_pay = self.env['employee.advance'].sudo().search_count(
            [('state','in',['approved'])])
        # timesheets = self.env['account.analytic.line'].sudo().search_count(
        #     [('project_id', '!=', False), ])
        timesheets_self = self.env['account.analytic.line'].sudo().search_count(
            [('project_id', '!=', False), ('user_id', '=', uid)])
        job_applications = self.env['hr.applicant'].sudo().search_count([])
        timesheet_verify = self.env['timesheet.checklist'].search_count([
            ('state', '=', 'manager_approval')])
        timesheet_approve = self.env['timesheet.checklist'].search_count([
            ('state', '=', 'hr_approval')])

        # payroll Datas for Bar chart
        query = """
            select to_char(to_timestamp (date_part('month', p.date_from)::text, 'MM'), 'Month') as Month, sum(pl.amount)
            as Total from hr_payslip p
            INNER JOIN hr_payslip_line pl
                on (p.id = pl.slip_id and pl.code = 'NET' and p.state = 'done')
            group by month, p.date_from order by p.date_from
        """
        cr.execute(query)
        payroll_data = cr.dictfetchall()
        payroll_label = []
        payroll_dataset = []
        for data in payroll_data:
            payroll_label.append(data['month'])
            payroll_dataset.append(data['total'])

        query = """
            select e.name as employee, j.name as job, d.name as department,
            e.work_phone, e.work_email, e.work_location, e.gender, e.birthday, e.marital, e.passport_id,
            e.medic_exam, e.public_info from hr_employee e inner join hr_job j on (j.id = job_id)
            inner join hr_department d on (e.department_id = d.id)
        """
        cr.execute(query)
        employee_table = cr.dictfetchall()
        if employee_id:
            categories = self.env['hr.employee.category'].sudo().search([
                ('id', 'in', employee_id[0]['category_ids'])])
            data = {
                'categories': [c.name for c in categories],
                'leave_search_view_id': leave_search_view_id.id,
                'leave_summary_view_id': leave_summary_view_id.id,
                'leaves_to_approve': leaves_to_approve,
                'leaves_alloc_to_approve': leaves_alloc_to_approve,
                'is_leave_manager': is_leave_manager,
                'timesheet_search_view_id': timesheet_search_view_id.id,
                'job_search_view_id': job_search_view_id.id,
                'is_timesheet_verify': is_timesheet_verify,
                'timesheet_verify': timesheet_verify,
                'timesheet_approve': timesheet_approve,
                'is_timesheet_approve': is_timesheet_approve,
                'expense_search_view_id': expense_search_view_id.id,
                'is_expense_manager': is_expense_manager,
                'is_expense_finance': is_expense_finance,
                'expense_to_pay': expense_to_pay,
                'expenses_to_approve': expenses_to_approve,
                'is_advance_manager': is_advance_manager,
                'advance_to_approve': advance_to_approve,
                'is_advance_finance': is_advance_finance,
                'advance_to_pay': advance_to_pay,
                # 'timesheets_request': timesheets_request,
                'timesheets_user': timesheets_self,
                'job_applications': job_applications,
                'payroll_label': payroll_label,
                'payroll_dataset': payroll_dataset,
                'emp_table': employee_table,
            }
            employee_id[0].update(data)
        return employee_id

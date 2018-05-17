# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'HR Timesheet ESS',
    'version' : '1.0',
    'summary': 'HRMS',
    'description': """
Human Resource Management System
=================================
- Employee Timesheet Management
    """,
    'category': 'Hr',
    'website': '',
    'depends' : ['base', 'web', 'hr_timesheet', 'project', 'hr_payroll',
                 'emp_self_services'],
    'data': [
        'security/user_groups.xml',
        'security/ir.model.access.csv',
        'wizard/hr_timesheet_refuse_view.xml',
        'views/hr_timesheet_view.xml',
        'views/timesheet_checklist_view.xml',
        'views/timesheet_checklist_trip_sequence.xml',
        'views/hr_payslip_view.xml',
        'reports/timesheet_report.xml',
        'views/register_report.xml',
        'views/menuitems_view.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

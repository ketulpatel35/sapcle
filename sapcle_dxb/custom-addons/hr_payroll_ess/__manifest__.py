# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Payroll ESS',
    'version' : '1.0',
    'summary': 'HR Payroll ESS',
    'description': """
Payroll ESS
=================================
- Manage Employee Payroll
    """,
    'category': 'Hr',
    'website': '',
    'depends' : ['base', 'hr_payroll', 'emp_self_services', 'account'],
    'data': [
        'security/user_groups.xml',
        'security/ir.model.access.csv',
        'reports/payslip_report.xml',
        'views/hr_payroll_sequence.xml',
        'views/register_report.xml',
        'views/hr_payslip_view.xml',
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

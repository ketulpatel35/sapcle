# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'HR Employee Advance',
    'version' : '1.0',
    'summary': 'HRMS',
    'description': """
HR Employee Advance ESS
=================================
- HR Employee Advance Management
    """,
    'category': 'Hr',
    'website': '',
    'depends' : ['base', 'hr', 'hr_payroll', 'emp_self_services'],
    'data': [
        'security/user_groups.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'wizard/hr_advance_refuse_view.xml',
        'views/hr_emp_advance_view.xml',
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

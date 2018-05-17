# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'HR Expense ESS',
    'version' : '1.0',
    'summary': 'HRMS',
    'description': """
HR Expense ESS
=================================
- Manage Expense
    """,
    'category': 'Hr',
    'website': '',
    'depends' : ['base', 'hr', 'hr_expense', 'emp_self_services'],
    'data': [
        'security/hr_expense_security.xml',
        'security/ir.model.access.csv',
        'wizard/hr_expense_refuse_view.xml',
        'views/hr_expence_view.xml',
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

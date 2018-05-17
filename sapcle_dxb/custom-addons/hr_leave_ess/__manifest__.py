# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Leave ESS',
    'version' : '1.0',
    'summary': 'HR Leave ESS',
    'description': """
Employee Leave Management ESS
=================================
- Manage Employee Leave
    """,
    'category': 'Hr',
    'website': '',
    'depends' : ['base', 'hr_holidays', 'emp_self_services'],
    'data': [
        'security/hr_holidays_security.xml',
        'security/ir.model.access.csv',
        'views/hr_leaves_view.xml',
        'views/hr_holiday_status_view.xml',
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

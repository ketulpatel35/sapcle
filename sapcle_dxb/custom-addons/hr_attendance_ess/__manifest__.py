# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'HR Attendance ESS',
    'version' : '1.0',
    'summary': 'HRMS',
    'description': """
Employee Attendance ESS
=================================
- Manage Employee Attendance
    """,
    'category': 'Hr',
    'website': '',
    'depends' : ['base', 'hr', 'hr_attendance', 'emp_self_services'],
    'data': [
        # 'security/account_security.xml',
        # 'security/ir.model.access.csv',
        'views/hr_attendance_view.xml',
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

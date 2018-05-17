# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Employee Self Service',
    'version' : '1.0',
    'summary': 'HRMS',
    'description': """
Human Resource Management System
=================================
- Employee Profile
    """,
    'category': 'Hr',
    'website': '',
    'depends' : ['base', 'hr', 'mail', 'web', 'website', 'contacts'],
    'data': [
        'security/hr_security.xml',
        'security/ir.model.access.csv',
        'views/employee_documents_view.xml',
        'views/employee_profile_view.xml',
        'views/menuitems_view.xml',
        'views/hide_powred_by.xml',
    ],
    'demo': [
    ],
    'qweb': [
        # "static/src/xml/hide_everybody_calendars.xml",
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

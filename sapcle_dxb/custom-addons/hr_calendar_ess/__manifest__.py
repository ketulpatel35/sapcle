# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'HR Calendar',
    'version' : '1.0',
    'summary': 'HRMS',
    'description': """
HR Calendar
=================================
- HR Calendar
    """,
    'category': 'Hr',
    'website': '',
    'depends' : ['base', 'calendar', 'web'],
    'data': [
        'views/calendar_view.xml',
        'views/load_scripts.xml',
    ],
    'demo': [
    ],
    'qweb': [
        # 'static/src/xml/hide_everybody_calendars.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

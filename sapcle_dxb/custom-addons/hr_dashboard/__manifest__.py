# -*- coding: utf-8 -*-
##############################################################################
# Ketul & Lithin
##############################################################################
{
    'name': "Employee Dashboard",

    'summary': """
        Dashboard For All Employees.
        """,

    'description': """
        Dashboard which includes employee details,
        menus and count of approvals needed and logged in user details
    """,
    'author': "Ketul Patel",
    'website': "",
    'category': "Generic Modules/Human Resources",
    'version': "11.0.1.0.0",
    'depends': [
        'base', 'hr', 'website_hr', 'hr_timesheet_ess', 'hr_leave_ess',
        'hr_expense', 'hr_expense_ess', 'hr_emp_advance'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_dashboard.xml',
        'views/hr_employee_views.xml',
    ],
    'qweb': [
        "static/src/xml/hr_dashboard.xml",
    ],
    'images': [],
    'license': "AGPL-3",
    'installable': True,
    'application': True,
}

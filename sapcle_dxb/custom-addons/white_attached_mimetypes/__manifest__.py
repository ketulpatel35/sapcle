# -*- encoding: utf-8 -*-
##############################################################################
#
##############################################################################
{
    'name': 'White Attached Mimetype',
    'version': '1.1',
    'summary': 'White Attached Mimetype',
    'sequence': 30,
    'description': """
    White Attached Mimetype
""",
    'author': 'sapcle',
    'website': '',
    'images': [],
    'depends': ['base', 'document'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_company_view.xml',
        'views/white_mimetype_view.xml',
        'views/white_mimetype_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

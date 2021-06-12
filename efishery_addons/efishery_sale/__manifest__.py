# -*- coding: utf-8 -*-
{
    'name': 'Efishery Sale',
    "license": "LGPL-3",
    'summary': """
        Efishery Sale
        """,
    'description': """
        Efishery Sale Endpoint/API to create, update, get data
    """,
    'images': ['static/description/icon.png'],
    'author': "Rehan | Fahmi Roihanul Firdaus",
    'website': "https://www.efishery.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'sale_management'],
    'data': [
        'views/sale_views.xml',
        'views/res_config_views.xml'
    ]
}
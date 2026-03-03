{
    'name': 'New Property Management App',
    'version': '1.0.0',
    'summary': 'Simple real estate property management',
    'category': 'Tools',
    'author': 'Your Name',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_menus.xml',
        'views/res_users_views.xml',
    ],
    'application': True,
    'installable': True,
}

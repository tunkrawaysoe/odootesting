{
    'name': 'New Custom Project Updates',
    'version': '1.0',
    'depends': ['project', 'web'],
    'data': [
        'views/project_task_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'custom_project_updates/static/src/dashboard/dashboard.js',
            'custom_project_updates/static/src/dashboard/dashboard.xml',
            'custom_project_updates/static/src/dashboard/dashboard.scss',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
{
    'name': 'OWL Todo List New',
    'version': '1.0',
    'category': 'Tool',
    'depends': ['base', 'web'],
    'data': [
        'views/todo_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'owl_todo/static/src/components/**/*.js',
            'owl_todo/static/src/components/**/*.xml',
            'owl_todo/static/src/components/**/*.scss',
            'owl_todo/static/src/main.js',
        ],
    },
    'installable': True,
    'application': True,
}
{
    'name': 'BSS Student Access Rights',
    'version': '1.0',
    'summary': 'User access control for Student Module',
    'description': 'Restrict student module access based on user groups.',
    'category': 'Education',
    'author': 'Your Name',
    'depends': ['bss_student'], 
    'data': [
        'security/bss_student_security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

# -*- coding: utf-8 -*-
{
    "name": "Member Management 11",
    "version": "19.0.1.0.0",
    "category": "Website",
    "summary": "Member registration + approval workflow extending Contacts (res.partner)",
    "depends": ["contacts", "website",],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_views.xml",
        "templates/member_register.xml",
        "data/website_menu.xml",
    ],
    "application": True,
    "license": "LGPL-3",
}

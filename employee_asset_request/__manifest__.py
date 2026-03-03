# -*- coding: utf-8 -*-
{
    "name": "Employee Asset Request New",
    "summary": "Asset Request & Assignment Workflow",
    "version": "19.0.1.0.1",
    "category": "Human Resources",
    "author": "Your Company",
    "license": "LGPL-3",
    "depends": ["base", "hr", "mail"],
    "data": [
        "security/asset_groups.xml",
        "security/ir.model.access.csv",
        "security/asset_request_rules.xml",
        "data/sequence.xml",
        "views/employee_asset_views.xml",
        "views/asset_assignment_wizard_views.xml",
        "views/asset_request_views.xml",
        "views/asset_request_report_views.xml",
        "views/menus.xml",
    ],
    "installable": True,
    "application": True,
}

from odoo import models, fields

class Subject(models.Model):
    _name = "bss.subject"
    _description = "Subject"

    name = fields.Char(required=True)

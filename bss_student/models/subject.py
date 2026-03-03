from odoo import models, fields

class BssSubject(models.Model):
    _name = 'bss.subject'
    _description = 'Subject'

    name = fields.Char(string="Subject Name", required=True)
    description = fields.Text(string="Description")
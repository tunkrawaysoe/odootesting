from odoo import models, fields, api

class Class(models.Model):
    _name = "bss.class"
    _description = "Class"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    subject_ids = fields.Many2many("bss.subject", string="Subjects")

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Class code must be unique')
    ]

    def name_get(self):
        result = []
        for rec in self:
            name = f"{rec.name} ({rec.code})"
            result.append((rec.id, name))
        return result

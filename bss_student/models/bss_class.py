from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BssClass(models.Model):
    _name = "bss.class"
    _description = "Class"
    _rec_name = "name_display"

    name = fields.Char(string="Class Name", required=True)
    code = fields.Char(string="Class Code", required=True)
    subject_ids = fields.Many2many("bss.subject", string="Subjects")
    description = fields.Text(string="Description")

    # Avoid defining Odoo's special field name 'display_name'
    name_display = fields.Char(string="Display Name", compute="_compute_name_display", store=True)

    _unique_class_code = models.Constraint(
    'UNIQUE(code)',
    'Class Code must be unique.'
)

    @api.depends("name", "code")
    def _compute_name_display(self):
        for record in self:
            record.name_display = f"{record.name} ({record.code})" if record.code else record.name

    @api.constrains("code")
    def _check_unique_code(self):
        # Keep a friendly ValidationError message (SQL constraint will also protect)
        for record in self:
            if record.code:
                existing = self.search([("code", "=", record.code), ("id", "!=", record.id)], limit=1)
                if existing:
                    raise ValidationError(f"The code '{record.code}' already exists for another class.")

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Real Estate Property Type"
    _order = "name"

    name = fields.Char(required=True)

    # ✅ Database-level UNIQUE (exact match protection)
    _unique_name = models.Constraint(
        'UNIQUE(name)',
        'The property type name must be unique.'
    )

    # ✅ Case-insensitive + trimmed uniqueness (ORM level)
    @api.constrains('name')
    def _check_unique_name_ci(self):
        for record in self:
            if not record.name:
                continue

            name = record.name.strip()

            existing = self.search([
                ('id', '!=', record.id),
                ('name', '=ilike', name),
            ], limit=1)

            if existing:
                raise ValidationError(
                    _("The property type name must be unique (case-insensitive).")
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name'):
                vals['name'] = vals['name'].strip()
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('name'):
            vals['name'] = vals['name'].strip()
        return super().write(vals)
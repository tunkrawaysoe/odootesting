from odoo import models, fields, api
from odoo.exceptions import ValidationError

class AssetAssignmentWizard(models.TransientModel):
    _name = "asset.assignment.wizard"
    _description = "Asset Assignment Wizard"

    request_id = fields.Many2one(
        "employee.asset.request",
        string="Request",
        required=True,
        readonly=True,
    )

    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        readonly=True,
    )

    asset_type = fields.Selection(
        related="request_id.asset_type",
        readonly=True,
    )

    quantity = fields.Integer(
        related="request_id.quantity",
        readonly=True,
    )

    asset_ids = fields.Many2many(
        "employee.asset",
        string="Assets to Assign",
        domain="[('state','=','available'), ('asset_type','=',asset_type)]",
        help="Select available assets of the requested type. Creation is disabled.",
    )

    no_assets_message = fields.Char(
        string="Info",
        compute="_compute_no_assets_message",
        readonly=True,
    )

    @api.depends('asset_type')
    def _compute_no_assets_message(self):
        for rec in self:
            available_count = self.env['employee.asset'].search_count([
                ('state', '=', 'available'),
                ('asset_type', '=', rec.asset_type)
            ])
            if not available_count:
                rec.no_assets_message = "⚠️ No available assets of this type."
            else:
                rec.no_assets_message = False

    def action_confirm_assignment(self):
        self.ensure_one()

        if self.request_id.state != "approved":
            raise ValidationError("This request is not in Approved state anymore.")

        # Check if any assets selected
        if not self.asset_ids:
            raise ValidationError("Cannot assign: no available assets of the requested type.")

        # Validate quantity
        if len(self.asset_ids) != self.quantity:
            raise ValidationError(
                f"Selected assets ({len(self.asset_ids)}) must equal requested quantity ({self.quantity})."
            )

        # Validate availability (race condition)
        for asset in self.asset_ids:
            if asset.state != "available":
                raise ValidationError(
                    f"Asset {asset.name} is no longer available."
                )

        # Assign assets
        self.asset_ids.write({
            "state": "assigned",
            "assigned_employee_id": self.employee_id.id,
        })

        # Update request
        self.request_id.write({
            "state": "assigned",
            "assignment_date": fields.Date.today(),
            "asset_ids": [(6, 0, self.asset_ids.ids)],
        })

        # Log in chatter
        self.request_id.message_post(
            body=("✅ Assets assigned: " + ", ".join(self.asset_ids.mapped("name")))
        )

        return {"type": "ir.actions.act_window_close"}
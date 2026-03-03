from odoo import models, fields, api
from odoo.exceptions import ValidationError

# Employee Asset Model
class EmployeeAsset(models.Model):
    _name = "employee.asset"
    _description = "Employee Asset"
    _inherit = ["mail.thread"]
    _order = "id desc"

    name = fields.Char(required=True, tracking=True)
    serial_number = fields.Char(tracking=True)

    asset_type = fields.Selection([
        ("laptop", "Laptop"),
        ("phone", "Phone"),
        ("monitor", "Monitor"),
        ("other", "Other"),
    ], required=True, tracking=True)

    state = fields.Selection([
        ("available", "Available"),
        ("assigned", "Assigned"),
        ("maintenance", "Maintenance"),
        ("retired", "Retired"),
    ], default="available", tracking=True)

    assigned_employee_id = fields.Many2one(
        "hr.employee", string="Assigned Employee", tracking=True
    )

    request_count = fields.Integer(
        compute="_compute_request_count", string="Requests"
    )

    request_id = fields.Many2one(
        'employee.asset.request',
        string="Asset Request"
    )

    # Compute request count
    @api.depends()
    def _compute_request_count(self):
        if not self:
            return
        request_data = self.env["employee.asset.request"].read_group(
            [("asset_ids", "in", self.ids)],
            ["asset_ids"],
            ["asset_ids"]
        )
        mapped_data = {
            data["asset_ids"][0]: data["asset_ids_count"]
            for data in request_data
        }
        for rec in self:
            rec.request_count = mapped_data.get(rec.id, 0)

    # -----------------------------
    # Manual state actions
    # -----------------------------
    def action_mark_available(self):
        self.write({"state": "available", "assigned_employee_id": False})

    def action_mark_maintenance(self):
        self.write({"state": "maintenance"})

    def action_retire(self):
        self.write({"state": "retired"})


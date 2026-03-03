from odoo import models, fields, api
from odoo.exceptions import ValidationError

class EmployeeAssetRequest(models.Model):
    _name = "employee.asset.request"
    _description = "Employee Asset Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(default="New", copy=False, readonly=True)

    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        required=True,
        default=lambda self: self.env.user.employee_id or False,
        tracking=True
    )

    manager_id = fields.Many2one(
        "hr.employee",
        string="Approving Manager",
        compute="_compute_manager",
        store=True,
        readonly=True
    )

    asset_type = fields.Selection([
        ("laptop", "Laptop"),
        ("phone", "Phone"),
        ("monitor", "Monitor"),
        ("other", "Other"),
    ], required=True, tracking=True)

    quantity = fields.Integer(default=1, required=True, tracking=True)
    reason = fields.Text(required=True)

    asset_ids = fields.Many2many(
        "employee.asset",
        string="Assigned Assets"
    )

    state = fields.Selection([
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("assigned", "Assigned"),
    ], default="draft", tracking=True)

    assignment_date = fields.Date(readonly=True)

    is_current_manager = fields.Boolean(
        compute="_compute_is_current_manager"
    )

    # Compute manager and check
    @api.depends("employee_id")
    def _compute_manager(self):
        for rec in self:
            rec.manager_id = rec.employee_id.parent_id

    @api.depends("manager_id")
    def _compute_is_current_manager(self):
        for rec in self:
            rec.is_current_manager = (
                rec.manager_id
                and rec.manager_id.user_id
                and rec.manager_id.user_id == self.env.user
            )

    # Constraints
    @api.constrains("quantity")
    def _check_quantity(self):
        for rec in self:
            if rec.quantity <= 0:
                raise ValidationError("Quantity must be greater than 0.")

    # Actions
    def action_submit(self):
        for rec in self:
            if rec.state != "draft":
                raise ValidationError("Only draft requests can be submitted.")
            if not rec.employee_id:
                raise ValidationError(
                    "Your user is not linked to an Employee. Ask HR to link your user to an employee record."
                )
            if not rec.manager_id or not rec.manager_id.user_id:
                raise ValidationError(
                    "Employee must have a manager with a linked user."
                )
            rec.state = "submitted"

            note = (
                f"📌 Asset Request Submitted:\n"
                f"Employee: {rec.employee_id.name}\n"
                f"Type: {rec.asset_type.capitalize()}\n"
                f"Quantity: {rec.quantity}\n"
                f"Reason: {rec.reason[:50]}{'...' if len(rec.reason) > 50 else ''}\n"
                f"Please review and approve."
            )

            rec.activity_schedule(
                "mail.mail_activity_data_todo",
                user_id=rec.manager_id.user_id.id,
                note=note
            )

    def action_approve(self):
        for rec in self:
            if rec.manager_id.user_id != self.env.user:
                raise ValidationError(
                    "Only the assigned manager can approve this request."
                )
            if rec.state != "submitted":
                raise ValidationError(
                    "Only submitted requests can be approved."
                )

            # Close pending manager to-do activities created on submit
            rec.activity_feedback("mail.mail_activity_data_todo")

            rec.state = "approved"
            # Open assignment wizard
            return {
                "type": "ir.actions.act_window",
                "name": "Assign Assets",
                "res_model": "asset.assignment.wizard",
                "view_mode": "form",
                "target": "new",
                "context": {
                    "default_request_id": rec.id,
                    "default_employee_id": rec.employee_id.id,
                    "default_asset_type": rec.asset_type,
                    "default_quantity": rec.quantity,
                },
            }

    def action_reject(self):
        for rec in self:
            if rec.manager_id.user_id != self.env.user:
                raise ValidationError(
                    "Only the assigned manager can reject this request."
                )
            if rec.state != "submitted":
                raise ValidationError("Only submitted requests can be rejected.")

            # Close pending manager to-do activities created on submit
            rec.activity_feedback("mail.mail_activity_data_todo")

            rec.state = "rejected"

    def action_open_assignment_wizard(self):
        self.ensure_one()

        if self.state != 'approved':
            raise ValidationError("Only approved requests can be assigned.")
        if not self.is_current_manager:
            raise ValidationError("Only the assigned manager can assign assets.")

        return {
            'type': 'ir.actions.act_window',
            'name': 'Assign Assets',
            'res_model': 'asset.assignment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_request_id': self.id,
                'default_employee_id': self.employee_id.id,
                'default_asset_type': self.asset_type,
                'default_quantity': self.quantity,
            }
        }

    # Create sequence
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "employee.asset.request"
                ) or "New"
        return super().create(vals_list)
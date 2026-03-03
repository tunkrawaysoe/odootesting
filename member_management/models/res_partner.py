# -*- coding: utf-8 -*-
import base64
import re

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    dob = fields.Date(string="Date of Birth")

    gender = fields.Selection(
        [("male", "Male"), ("female", "Female"), ("other", "Other")],
        string="Gender",
    )

    marital_status = fields.Selection(
        [("single", "Single"), ("married", "Married"), ("divorced", "Divorced"), ("widowed", "Widowed")],
        string="Marital Status",
    )

    member_type = fields.Selection(
        [("supplier", "Supplier"), ("partner", "Partner"), ("member", "Member")],
        string="Member Type",
        default="member",
    )

    # Stored temporarily until accepted (then cleared)
    password = fields.Char(string="Password", password=True)
    confirm_password = fields.Char(string="Confirm Password", password=True)

    state = fields.Selection(
        [("draft", "Draft"), ("submitted", "Submitted"), ("accepted", "Accepted"), ("rejected", "Rejected")],
        string="Status",
        default="draft",
        tracking=True,
    )

    # ---------- Password Strength ----------
    def _check_password_strength(self, password):
        if not password:
            raise ValidationError(_("Password is required."))

        if len(password) < 8:
            raise ValidationError(_("Password must be at least 8 characters."))

        if not re.search(r"[A-Z]", password):
            raise ValidationError(_("Password must contain at least one uppercase letter."))

        if not re.search(r"[a-z]", password):
            raise ValidationError(_("Password must contain at least one lowercase letter."))

        if not re.search(r"\d", password):
            raise ValidationError(_("Password must contain at least one number."))

        if not re.search(r"[^\w\s]", password):
            raise ValidationError(_("Password must contain at least one special character (e.g. !@#$)."))

    # ---------- Constraints ----------
    @api.constrains("password", "confirm_password")
    def _check_password_match(self):
        for rec in self:
            # Only validate when user is entering password fields
            if rec.password or rec.confirm_password:
                if rec.password != rec.confirm_password:
                    raise ValidationError(_("Password and Confirm Password must match."))
                rec._check_password_strength(rec.password)

    # ---------- Business method for Website Registration ----------
    @api.model
    def create_member_from_webform(self, post, upload_file):
        """Validate + create res.partner with state=submitted (used by controller)."""

        required = ["name", "email", "password", "confirm_password", "member_type"]
        missing = [f for f in required if not post.get(f)]
        if missing:
            raise ValidationError(_("Missing required fields: %s") % ", ".join(missing))

        if post.get("password") != post.get("confirm_password"):
            raise ValidationError(_("Password and Confirm Password must match."))

        self._check_password_strength(post.get("password"))

        if not upload_file:
            raise ValidationError(_("Profile image is required."))

        # Avoid duplicate partner email
        if self.sudo().search([("email", "=", post.get("email"))], limit=1):
            raise ValidationError(_("A member/contact with this email already exists."))

        image_b64 = base64.b64encode(upload_file.read())

        vals = {
            "name": post.get("name"),
            "email": post.get("email"),
            "phone": post.get("phone"),
            "dob": post.get("dob") or False,
            "gender": post.get("gender") or False,
            "marital_status": post.get("marital_status") or False,
            "member_type": post.get("member_type") or "member",
            "password": post.get("password"),
            "confirm_password": post.get("confirm_password"),
            "image_1920": image_b64,
            "street": post.get("street") or False,
            "city": post.get("city") or False,
            "country_id": int(post["country_id"]) if post.get("country_id") else False,
            "state": "submitted",
        }
        return self.sudo().create(vals)

    # ---------- Workflow Buttons ----------
    def action_accept_member(self):
        Users = self.env["res.users"].sudo()

        for rec in self:
            if rec.state != "submitted":
                continue

            if not rec.email:
                raise UserError(_("Email is required to create a user."))

            if not rec.password:
                raise UserError(_("Password is required to create a user."))

            # Safety: check strength again
            rec._check_password_strength(rec.password)

            existing = Users.search([("login", "=", rec.email)], limit=1)
            if existing:
                raise UserError(_("A user with this email/login already exists: %s") % rec.email)

            user_vals = {
                "name": rec.name,
                "login": rec.email,
                "password": rec.password,
                "partner_id": rec.id,
            }

            # Bulletproof: keep only valid fields (avoids groups_id issues)
            safe_vals = {k: v for k, v in user_vals.items() if k in Users._fields}
            Users.create(safe_vals)

            rec.write({
                "state": "accepted",
                "password": False,
                "confirm_password": False,
            })

    def action_reject_member(self):
        for rec in self:
            rec.write({
                "state": "rejected",
                "password": False,
                "confirm_password": False,
            })
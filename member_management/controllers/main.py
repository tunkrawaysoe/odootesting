from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError


class MemberRegistrationController(http.Controller):

    @http.route("/member/register", type="http", auth="public", website=True, methods=["GET"])
    def member_register_get(self, **kw):
        countries = request.env["res.country"].sudo().search([])
        return request.render("member_management.member_register_template", {
            "countries": countries,
            "error": None,
            "success": None,
            "values": {},
        })

    @http.route("/member/register", type="http", auth="public", website=True, methods=["POST"], csrf=True)
    def member_register_post(self, **post):
        countries = request.env["res.country"].sudo().search([])
        values = dict(post)

        upload = request.httprequest.files.get("profile_image")

        try:
            request.env["res.partner"].create_member_from_webform(post, upload)
        except ValidationError as e:
            # Don’t keep passwords in the form after error (safer UX)
            values.pop("password", None)
            values.pop("confirm_password", None)
            return request.render("member_management.member_register_template", {
                "countries": countries,
                "error": str(e),
                "success": None,
                "values": values,
            })

        return request.render("member_management.member_register_template", {
            "countries": countries,
            "error": None,
            "success": "Registration submitted successfully. Please wait for approval.",
            "values": {},
        })
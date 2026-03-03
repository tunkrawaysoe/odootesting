from odoo import models, fields, api


class BssAttendance(models.Model):
    _name = "bss.attendance"
    _description = "Attendance"

    attendance_number = fields.Char(string="Attendance Number", readonly=True, copy=False)

    student_id = fields.Many2one("bss.student", string="Student", required=True)

    # Auto-follow student's class to prevent mismatches.
    class_id = fields.Many2one(
        "bss.class",
        string="Class",
        related="student_id.class_id",
        store=True,
        readonly=True,
    )

    date = fields.Date(string="Date", default=fields.Date.today)
    status = fields.Selection(
        [("present", "Present"), ("absent", "Absent"), ("late", "Late")],
        string="Status",
        default="present",
    )
    notes = fields.Text(string="Notes")

    _sql_constraints = [
        ("attendance_number_uniq", "unique(attendance_number)", "Attendance Number must be unique."),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("attendance_number"):
                vals["attendance_number"] = self.env["ir.sequence"].next_by_code("bss.attendance") or "ATD/0001"
        return super().create(vals_list)

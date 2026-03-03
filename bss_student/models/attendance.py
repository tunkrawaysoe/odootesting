from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BssAttendance(models.Model):
    _name = "bss.attendance"
    _description = "Attendance"

    attendance_number = fields.Char(string="Attendance Number", readonly=True, copy=False)

    student_id = fields.Many2one("bss.student", string="Student", required=True)

    class_id = fields.Many2one(
        "bss.class",
        string="Class",
        related="student_id.class_id",
        store=True,
        readonly=True,
    )

    date = fields.Date(string="Date", default=fields.Date.today, required=True)

    status = fields.Selection(
        [("present", "Present"), ("absent", "Absent"), ("late", "Late")],
        string="Status",
        default="present",
        required=True,
    )

    notes = fields.Text(string="Notes")

    # ✅ UNIQUE attendance number
    _unique_attendance_number = models.Constraint(
        "UNIQUE(attendance_number)",
        "Attendance Number must be unique."
    )

    # ✅ Only one attendance per student per day
    _unique_student_date = models.Constraint(
        "UNIQUE(student_id, date)",
        "Attendance already exists for this student on this date."
    )

    @api.constrains("date")
    def _check_date_not_future(self):
        today = fields.Date.today()
        for rec in self:
            if rec.date and rec.date > today:
                raise ValidationError("Attendance date cannot be in the future.")
            
    @api.constrains("student_id")
    def _check_student_has_class(self):
        for rec in self:
            if rec.student_id and not rec.student_id.class_id:
                raise ValidationError("You must set the student's class before creating attendance.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("attendance_number"):
                seq = self.env["ir.sequence"].next_by_code("bss.attendance")
                if not seq:
                    raise ValidationError("Attendance sequence (bss.attendance) is missing.")
                vals["attendance_number"] = seq
        return super().create(vals_list)
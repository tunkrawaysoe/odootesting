from odoo import models, fields, api


class BssStudent(models.Model):
    _name = "bss.student"
    _description = "Student"

    name = fields.Char(string="Student Name", required=True)
    student_number = fields.Char(string="Student Number", readonly=True, copy=False)

    # Parent/guardian contact
    contact_person_id = fields.Many2one("res.partner", string="Parent Contact")

    class_id = fields.Many2one("bss.class", string="Class")
    subject_ids = fields.Many2many("bss.subject", string="Subjects")

    # Student login user
    user_id = fields.Many2one("res.users", string="Related User")

    _unique_student_number = models.Constraint(
        "UNIQUE(student_number)",
        "Student Number must be unique.",
    )

    def _sync_user_name(self):
        """Sync student.name -> related user's partner name."""
        for student in self:
            if student.user_id and student.name:
                # res.users name is partner name, so write partner_id.name
                student.user_id.partner_id.with_context(skip_student_user_sync=True).write({
                    "name": student.name
                })

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("student_number"):
                vals["student_number"] = (
                    self.env["ir.sequence"].next_by_code("bss.student") or "STD/0001"
                )

        students = super().create(vals_list)

        # sync after create (if user_id set)
        students._sync_user_name()
        return students

    def write(self, vals):
        res = super().write(vals)

        # sync if student name changed or user changed
        if not self.env.context.get("skip_student_user_sync") and any(
            k in vals for k in ("name", "user_id")
        ):
            self._sync_user_name()

        return res

    @api.onchange("class_id")
    def _onchange_class_id(self):
        if self.class_id:
            self.subject_ids = [(6, 0, self.class_id.subject_ids.ids)]
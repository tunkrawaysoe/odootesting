from odoo import models, fields, api

class Student(models.Model):
    _name = "bss.student"
    _description = "Student"

    name = fields.Char(required=True)
    student_number = fields.Char(string="Student Number", readonly=True, copy=False, default="New")
    class_id = fields.Many2one("bss.class", string="Class")
    subject_ids = fields.Many2many("bss.subject", string="Subjects")
    contact_id = fields.Many2one("res.partner", string="Contact Person")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('student_number', 'New') == 'New':
                vals['student_number'] = self.env['ir.sequence'].next_by_code('bss.student.sequence') or 'New'
        
        
        return super(Student, self).create(vals_list)

    @api.onchange('class_id')
    def _onchange_class_id(self):
        """Auto-fill subjects based on the selected class."""
        if self.class_id:
            self.subject_ids = [(6, 0, self.class_id.subject_ids.ids)]
        else:
            self.subject_ids = [(5, 0, 0)]

    @api.onchange('name')
    def _onchange_name(self):
        """Update contact name to match student name if contact exists."""
        if self.name and self.contact_id:
            self.contact_id.name = self.name
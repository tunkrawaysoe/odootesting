from odoo import models, fields, api

class Attendance(models.Model):
    _name = "bss.attendance"
    _description = "Attendance"

    name = fields.Char(string="Attendance Name")
    attendance_number = fields.Char(string="Attendance Number", readonly=True, copy=False, default="New")
    student_id = fields.Many2one("bss.student", string="Student")
    class_id = fields.Many2one("bss.class", string="Class")

    @api.model_create_multi
    def create(self, vals_list):
        # vals_list is a list of dictionaries, e.g., [{'name': 'Math'}, {'name': 'Science'}]
        for vals in vals_list:
            if vals.get('attendance_number', 'New') == 'New':
                vals['attendance_number'] = self.env['ir.sequence'].next_by_code('bss.attendance.sequence') or 'New'
        
        # Pass the entire list to the parent create method
        return super(Attendance, self).create(vals_list)
from odoo import models, fields

class ProjectTask(models.Model):
    _inherit = 'project.task'

    is_urgent = fields.Boolean(string="Is Urgent?", default=False)
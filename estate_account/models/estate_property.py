from odoo import models, Command
from odoo.exceptions import UserError

class EstatePropertyInherit(models.Model):
    _inherit = "estate.property"

    def action_sold(self):
        for record in self:
            # 1️⃣ Validations
            if not record.buyer_id:
                raise UserError("You must set a buyer before selling the property.")
            if not record.selling_price:
                raise UserError("You must set a selling price before selling the property.")

        # 2️⃣ Call parent method to change state to 'sold'
        result = super().action_sold()

        for record in self:
            # 3️⃣ Find a Sales Journal
            journal = self.env['account.journal'].search([
                ('type', '=', 'sale'),
                ('company_id', '=', self.env.company.id)
            ], limit=1)
            if not journal:
                raise UserError("No Sales Journal found.")

            # 4️⃣ Create the invoice
            invoice = self.env['account.move'].create({
                'partner_id': record.buyer_id.id,  # Invoice for buyer
                'move_type': 'out_invoice',        # Customer invoice
                'journal_id': journal.id,
                'invoice_origin': record.name,     # Property name
                'invoice_line_ids': [
                    # 4a. Property Sale Price
                    Command.create({
                        'name': f'Property Sale: {record.name}',
                        'quantity': 1,
                        'price_unit': record.selling_price,
                    }),
                    # 4b. Commission (6%)
                    Command.create({
                        'name': 'Commission (6%)',
                        'quantity': 1,
                        'price_unit': record.selling_price * 0.06,
                    }),
                    # 4c. Administrative fees
                    Command.create({
                        'name': 'Administrative fees',
                        'quantity': 1,
                        'price_unit': 100.00,
                    }),
                ]
            })

            # 5️⃣ Optional: auto-post invoice
            invoice.action_post()  # if you want it posted immediately

        return result
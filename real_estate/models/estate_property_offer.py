from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"
    _order = "price desc"

    price = fields.Float(required=True)

    status = fields.Selection([
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('refused', 'Refused'),
    ], default='pending', copy=False, readonly=True)

    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
        required=True
    )

    property_id = fields.Many2one(
        "estate.property",
        string="Property",
        required=True
    )

    validity = fields.Integer(string="Validity (days)", default=7)

    date_deadline = fields.Date(
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline",
        store=True
    )

    # ✅ SQL constraint : offer price strictly positive
    _check_price_positive = models.Constraint(
        'CHECK(price > 0)',
        'Offer price must be strictly positive.'
    )

    # -------------------------
    # COMPUTE DEADLINE
    # -------------------------
    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                create_date = record.create_date.date()
                record.date_deadline = create_date + timedelta(days=record.validity or 0)
            else:
                record.date_deadline = fields.Date.today() + timedelta(days=record.validity or 0)

    def _inverse_date_deadline(self):
        for record in self:
            if record.create_date and record.date_deadline:
                create_date = record.create_date.date()
                record.validity = (record.date_deadline - create_date).days

    # OVERRIDE CREATE
    @api.model_create_multi
    def create(self, vals_list):

        max_price_by_property = {}

        for vals in vals_list:
            property_id = vals.get("property_id")
            price = vals.get("price") or 0.0

            if not property_id:
                continue

            prop = self.env["estate.property"].browse(property_id)

            if prop.state in ("sold", "canceled"):
                raise UserError(_("You cannot create an offer for a Sold or Canceled property."))

            if property_id not in max_price_by_property:
                max_price_by_property[property_id] = max(
                    prop.offer_ids.mapped("price"),
                    default=0.0
                )

            if price <= max_price_by_property[property_id]:
                raise UserError(_("The offer must be higher than the existing offers."))

            max_price_by_property[property_id] = price

        offers = super().create(vals_list)

        for offer in offers:
            if offer.property_id.state == "new":
                offer.property_id.state = "offer_received"

        return offers

    # ACTIONS
    def action_accept(self):
        today = fields.Date.today()

        for record in self:
            if record.status != 'pending':
                continue

            # ✅ Deadline business rule: cannot accept expired offer
            if record.date_deadline and record.date_deadline < today:
                raise UserError(_("You cannot accept an expired offer."))

            other_offers = record.property_id.offer_ids.filtered(lambda o: o.id != record.id)
            other_offers.write({'status': 'refused'})

            record.status = 'accepted'

            record.property_id.write({
                'selling_price': record.price,
                'buyer_id': record.partner_id.id,
                'state': 'offer_accepted',
            })

    def action_refuse(self):
        for record in self:
            if record.status == 'pending':
                record.status = 'refused'
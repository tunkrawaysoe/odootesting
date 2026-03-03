from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero
from datetime import timedelta

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(
        default=lambda self: fields.Date.today() + timedelta(days=90),
        copy=False
    )
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection([
        ('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')
    ])
    active = fields.Boolean(default=True)

    state = fields.Selection([
        ('new', 'New'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('canceled', 'Canceled'),
    ], default='new', required=True, copy=False)

    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    seller_id = fields.Many2one("res.users", string="Salesperson", default=lambda self: self.env.user)
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    total_area = fields.Integer(compute="_compute_total_area", string="Total Area")
    best_price = fields.Float(compute="_compute_best_price", string="Best Offer")

    # SQL constraints
    _check_expected_price_positive = models.Constraint(
        'CHECK(expected_price > 0)',
        'Expected price must be strictly positive.'
    )

    _check_selling_price_positive = models.Constraint(
        'CHECK(selling_price >= 0)',
        'Selling price must be positive.'
    )

    _unique_property_name = models.Constraint(
        'UNIQUE(name)',
        'Property name must be unique.'
    )

    # Computes
    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = (record.living_area or 0) + (record.garden_area or 0)

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            record.best_price = max(record.offer_ids.mapped("price"), default=0.0)

    # Onchange
    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = False

    # Python constraint 
    @api.constrains("selling_price", "expected_price")
    def _check_selling_price(self):
        for record in self:
            # selling_price is 0 until an offer is accepted
            if float_is_zero(record.selling_price, precision_rounding=0.01):
                continue

            min_price = record.expected_price * 0.9
            if float_compare(record.selling_price, min_price, precision_rounding=0.01) < 0:
                raise ValidationError(
                    _("Selling price cannot be lower than 90%% of expected price.")
                )

    # Clean name
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name'):
                vals['name'] = vals['name'].strip()
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('name'):
            vals['name'] = vals['name'].strip()
        return super().write(vals)

    # Delete protection
    @api.ondelete(at_uninstall=False)
    def _check_delete(self):
        for record in self:
            if record.state not in ('new', 'canceled'):
                raise UserError(_("You can only delete properties that are New or Canceled."))
            
    # Actions
    def action_sold(self):
        for record in self:
            if record.state != 'offer_accepted':
                raise UserError(_("You can only sell a property after accepting an offer."))
            record.state = 'sold'

    def action_cancel(self):
        for record in self:
            if record.state in ('sold', 'offer_accepted'):
                raise UserError(_("Cannot cancel a property that is sold or after accepting an offer."))
            record.state = 'canceled'
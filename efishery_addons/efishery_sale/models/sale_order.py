from odoo import fields, models

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    
    external_reference = fields.Char()
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    efishery_static_token = fields.Char(
        config_parameter='efishery.static_token',
        default='the_token'
    )
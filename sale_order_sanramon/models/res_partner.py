# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_tag = fields.Many2one(
        comodel_name="sale.order.tag", string="TagType", company_dependent=True
    )

    def copy_data(self, default=None):
        result = super().copy_data(default=default)
        for idx, partner in enumerate(self):
            values = result[idx]
            if partner.sale_tag and not values.get("sale_tag"):
                values["sale_tag"] = partner.sale_tag
        return result

# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    sale_tag_id = fields.Many2one(
        comodel_name="sale.order.tag",
        string="Sale Order Tag",
    )

    def _select(self):
        select_str = super()._select()
        select_str += """
            , move.sale_tag_id as sale_tag_id
            """
        return select_str

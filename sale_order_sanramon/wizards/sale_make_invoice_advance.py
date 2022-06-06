
from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _prepare_invoice_values(self, order, name, amount, so_line):
        res = super(SaleAdvancePaymentInv, self)._prepare_invoice_values(
            order, name, amount, so_line
        )
        if order.tag_id.journal_id:
            res["journal_id"] = order.tag_id.journal_id.id
        if order.tag_id:
            res["sale_tag_id"] = order.tag_id.id
        return res

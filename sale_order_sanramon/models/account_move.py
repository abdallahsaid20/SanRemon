# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Copyright 2020 Tecnativa - Pedro M. Baeza

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    sale_tag_id = fields.Many2one(
        comodel_name="sale.order.tag",
        string="Tag Type",
        compute="_compute_sale_tag_id",
        store=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        ondelete="restrict",
        copy=True,
    )

    @api.depends("partner_id", "company_id")
    def _compute_sale_tag_id(self):
        if not self.env.context.get("default_move_tag", False) or self.env.context.get(
            "active_model", False
        ) in ["sale.order", "sale.advance.payment.inv"]:
            return
        self.sale_tag_id = self.env["sale.order.tag"]
        for record in self:
            if record.move_tag not in ["out_invoice", "out_refund"]:
                record.sale_tag_id = self.env["sale.order.tag"]
                continue
            else:
                record.sale_tag_id = record.sale_tag_id
            if not record.partner_id:
                record.sale_tag_id = self.env["sale.order.tag"].search(
                    [("company_id", "in", [self.env.company.id, False])], limit=1
                )
            else:
                sale_tag = (
                    record.partner_id.with_company(record.company_id).sale_tag
                    or record.partner_id.commercial_partner_id.with_company(
                        record.company_id
                    ).sale_tag
                )
                if sale_tag:
                    record.sale_tag_id = sale_tag

    @api.onchange("sale_tag_id")
    def onchange_sale_tag_id(self):
        # TODO: To be changed to computed stored readonly=False if possible in v14?
        if self.sale_tag_id.payment_term_id:
            self.invoice_payment_term_id = self.sale_tag_id.payment_term_id.id
        if self.sale_tag_id.journal_id:
            self.journal_id = self.sale_tag_id.journal_id.id

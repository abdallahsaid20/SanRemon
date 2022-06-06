# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Copyright 2020 Tecnativa - Pedro M. Baeza

from datetime import datetime, timedelta

from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    tag_id = fields.Many2one(
        comodel_name="sale.order.tag",
        string="Tag type",
        compute="_compute_sale_tag_id",
        store=True,
        readonly=False,
        states={
            "sale": [("readonly", True)],
            "done": [("readonly", True)],
            "cancel": [("readonly", True)],
        },
        default=lambda so: so._default_tag_id(),
        ondelete="restrict",
        copy=True,
        check_company=True,
    )

    @api.model
    def _default_tag_id(self):
        return self.env["sale.order.tag"].search(
            [("company_id", "in", [self.env.company.id, False])], limit=1
        )

    @api.depends("partner_id", "company_id")
    def _compute_sale_tag_id(self):
        for record in self:
            if not record.partner_id:
                record.tag_id = self.env["sale.order.tag"].search(
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
                    record.tag_id = sale_tag

    @api.onchange("tag_id")
    def onchange_tag_id(self):
        # TODO: To be changed to computed stored readonly=False if possible in v14?
        vals = {}
        for order in self:
            order_tag = order.tag_id
            # Order values
            vals = {}
            if order_tag.warehouse_id:
                vals.update({"warehouse_id": order_tag.warehouse_id})
            if order_tag.picking_policy:
                vals.update({"picking_policy": order_tag.picking_policy})
            if order_tag.payment_term_id:
                vals.update({"payment_term_id": order_tag.payment_term_id})
            if order_tag.pricelist_id:
                vals.update({"pricelist_id": order_tag.pricelist_id})
            if order_tag.incoterm_id:
                vals.update({"incoterm": order_tag.incoterm_id})
            if order_tag.analytic_account_id:
                vals.update({"analytic_account_id": order_tag.analytic_account_id})
            if order_tag.quotation_validity_days:
                vals.update(
                    {
                        "validity_date": fields.Date.to_string(
                            datetime.now()
                            + timedelta(order_tag.quotation_validity_days)
                        )
                    }
                )
            if vals:
                order.update(vals)
            # Order line values
            line_vals = {}
            line_vals.update({"route_id": order_tag.route_id.id})
            order.order_line.update(line_vals)

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New") and vals.get("tag_id"):
            sale_tag = self.env["sale.order.tag"].browse(vals["tag_id"])
            if sale_tag.sequence_id:
                vals["name"] = sale_tag.sequence_id.next_by_id(
                    sequence_date=vals.get("date_order")
                )
        return super(SaleOrder, self).create(vals)

    def write(self, vals):
        """A sale tag could have a different order sequence, so we could
        need to change it accordingly"""
        if vals.get("tag_id"):
            sale_tag = self.env["sale.order.tag"].browse(vals["tag_id"])
            if sale_tag.sequence_id:
                for record in self:
                    if (
                        record.state in {"draft", "sent"}
                        and record.tag_id.sequence_id != sale_tag.sequence_id
                    ):
                        new_vals = vals.copy()
                        new_vals["name"] = sale_tag.sequence_id.next_by_id(
                            sequence_date=vals.get("date_order")
                        )
                        super(SaleOrder, record).write(new_vals)
                    else:
                        super(SaleOrder, record).write(vals)
                return True
        return super().write(vals)

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        if self.tag_id.journal_id:
            res["journal_id"] = self.tag_id.journal_id.id
        if self.tag_id:
            res["sale_tag_id"] = self.tag_id.id
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange("product_id")
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if self.order_id.tag_id.route_id:
            self.update({"route_id": self.order_id.tag_id.route_id})
        return res

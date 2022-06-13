from odoo import fields, models,_
from odoo.exceptions import UserError
from odoo.exceptions import AccessDenied



class SaleOrder(models.Model):
    _inherit = "sale.order"


    amount_due = fields.Monetary(related='partner_id.amount_due', currency_field='company_currency_id')
    company_currency_id = fields.Many2one(string='Company Currency', readonly=True,
                                          related='company_id.currency_id')

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('account_review', 'Approve For Sale Order'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status',
        readonly=True, copy=False, index=True, tracking=3, default='draft')
    in_approve = fields.Boolean('In Approve')

    def action_confirm(self):
        partner = self.partner_id
        partner_id = self.partner_id
        total_amount = self.amount_due
        if partner_id.credit_check:
            existing_move = self.env['account.move'].search(
                [('partner_id', '=', self.partner_id.id), ('state', '=', 'posted')])
            if partner_id.credit_blocking <= total_amount and not existing_move:
                view_id = self.env.ref('ob_customer_credit_limit.view_warning_wizard_form')
                context = dict(self.env.context or {})
                context['message'] = "Customer Blocking limit exceeded without having a recievable, Do You want to continue?"
                context['default_sale_id'] = self.id
                if not self._context.get('warning'):
                    return {
                        'name': 'Warning',
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'warning.wizard',
                        'view_id': view_id.id,
                        'target': 'new',
                        'context': context,
                    }
            elif partner_id.credit_warning == total_amount and partner_id.credit_blocking > total_amount:
                view_id = self.env.ref('ob_customer_credit_limit.view_warning_wizard_form')
                context = dict(self.env.context or {})
                context['message'] = "Customer warning limit exceeded, Do You want to continue?"
                context['default_sale_id'] = self.id
                if not self._context.get('warning'):
                    return {
                        'name': 'Warning',
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'warning.wizard',
                        'view_id': view_id.id,
                        'target': 'new',
                        'context': context,
                    }
            elif partner_id.credit_blocking == total_amount:

                view_id = self.env.ref(
                    'customer_credit_management.credit_management_limit_wizard').id
                return {
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sale.customer.credit.limit.wizard',
                    'target': 'new',
                    'type': 'ir.actions.act_window',
                    'name': 'Customer Credit Limit',
                    'views': [[view_id, 'form']],
                    'context': {'current_id': self.id}
                }
            else:
                credit = 0
                total_sales = 0
                sale_amt = 0
                inv_total_amt = 0
                inv_rec = self.env['account.move'].search([
                    ('partner_id', '=', partner.id),
                    ('state', 'not in', ['draft', 'cancel'])])
                sale_amount = self.search(
                    [('partner_id', '=', partner.id),
                     ]).mapped('amount_total')
                sale_amt = sum([sale for sale in sale_amount])
                for inv in inv_rec:
                    inv_total_amt += inv.amount_total - inv.amount_residual
                if partner.parent_id and partner.parent_id.credit < 0:
                    credit = partner.parent_id.credit
                elif partner.credit < 0:
                    credit = partner.credit
                total_sales = sale_amt + credit - inv_total_amt
                if total_sales > partner.credit_warning:
                    view_id = self.env.ref(
                        'customer_credit_management.credit_management_limit_wizard').id
                    return {
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'sale.customer.credit.limit.wizard',
                        'target': 'new',
                        'type': 'ir.actions.act_window',
                        'name': 'Customer Credit Limit',
                        'views': [[view_id, 'form']],
                        'context': {'current_id': self.id}
                    }
                else:
                    super(SaleOrder, self).action_confirm()
        else:
            super(SaleOrder, self).action_confirm()

    def action_account_approve(self):
        if self.env.user.has_group('sales_team.group_sale_manager'):
            super(SaleOrder, self).action_confirm()
        else:
            raise UserError((
                " Please contact your Administrator For SALE ORDER approval"))

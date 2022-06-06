

{
    "name": "Sale Order Tag",
    "version": "14.0.3.0.0",
    "category": "Sales Management",
    "depends": ["sale_stock", "account", "sale_management"],
    "demo": ["demo/sale_order_demo.xml"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/sale_order_view.xml",
        "views/sale_order_type_view.xml",
        "views/account_move_views.xml",
        "views/res_partner_view.xml",
        "data/default_type.xml",
        "reports/account_invoice_report_view.xml",
        "reports/sale_report_view.xml",
    ],
    "installable": True,
}

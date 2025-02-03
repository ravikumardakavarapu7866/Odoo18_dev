from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    shipping_fee = fields.Float(string='Shipping Fee', compute='_compute_shipping_fee', store=True)

    @api.depends('order_line.product_id', 'order_line.price_subtotal')
    def _compute_shipping_fee(self):
        for record in self:
            shipping_cost = 0.0

            for line in record.order_line:
                if line.product_id and line.product_id.name == "Standard delivery":
                    shipping_cost = line.price_subtotal

            linked_purchase_orders_count = self.env['purchase.order'].search_count([('origin', '=', record.name)])

            if shipping_cost > 0:
                if linked_purchase_orders_count > 0:
                    record.shipping_fee = shipping_cost / linked_purchase_orders_count
                else:
                    record.shipping_fee = shipping_cost
            else:
                record.shipping_fee = 0.0

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()

        for order in self:
            order._compute_shipping_fee()

            shipping_fee = order.shipping_fee or 0

            if shipping_fee > 0:
                purchase_orders = self.env['purchase.order'].search([('origin', '=', order.name)])

                for purchase_order in purchase_orders:
                    shipping_product = self.env['product.product'].search([('name', '=', 'Shipping Fee')], limit=1)

                    if shipping_product:
                        purchase_order.order_line.create({
                            'order_id': purchase_order.id,
                            'product_id': shipping_product.id,
                            'product_qty': 1,
                            'price_unit': shipping_fee,
                        })
        return res

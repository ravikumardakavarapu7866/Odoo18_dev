from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    platform_commission = fields.Float(string='Platform Commission', compute='_compute_platform_commission', store=True)

    @api.depends('product_id', 'price_subtotal')
    def _compute_platform_commission(self):
        for line in self:
            if line.product_id:
                commission_percentage = 0.0
                if line.product_id.seller_ids:
                    seller = line.product_id.seller_ids[0]
                    if seller.partner_id:
                        commission_percentage = seller.partner_id.commission_percentage

                if line.price_subtotal and commission_percentage:
                    line.platform_commission = (line.price_subtotal * commission_percentage) / 100
                else:
                    line.platform_commission = 0.0
            else:
                line.platform_commission = 0.0


class ResPartner(models.Model):
    _inherit = 'res.partner'

    commission_percentage = fields.Float(string='Commission %')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    total_platform_commission = fields.Float(string='Total Platform Commission',
                                             compute='_compute_total_platform_commission', store=True)

    @api.depends('order_line.platform_commission')
    def _compute_total_platform_commission(self):
        for order in self:
            total_commission = sum(line.platform_commission for line in order.order_line)
            order.total_platform_commission = total_commission


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    platform_commission_vendor = fields.Float(string='Platform Commission',
                                              compute='_compute_platform_commission_vendor', store=True)

    @api.depends('order_line.product_id', 'order_line.price_unit', 'order_line.product_qty')
    def _compute_platform_commission_vendor(self):
        for order in self:
            total_commission = 0.0
            for line in order.order_line:
                if line.product_id:
                    if line.product_id.name == "Shipping Fee":
                        continue

                    sale_price = line.product_id.lst_price
                    vendor_price = line.price_subtotal
                    commission = (sale_price - vendor_price)
                    total_commission += commission

            order.platform_commission_vendor = total_commission 

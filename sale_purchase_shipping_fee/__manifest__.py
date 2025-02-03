{
    'name': 'Sale Purchase Shipping Fee',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Add shipping fee from Sale Order to Purchase Order',
    'depends': ['sale', 'purchase','sale_management'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
}

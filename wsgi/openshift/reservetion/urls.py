from reservetion import views
from django.conf.urls import patterns, url
from django.conf import settings

urlpatterns = patterns('reservetion.views',

                       url(r'^menu/login/$', 'loginUser', name='loginUser'),
                       url(r'^menu/$', 'menu', name='menu'),

                       url(r'^sign/$', 'sign', name='sign'),
                       url(r'^login/$', 'loginUser', name='loginUser'),
                       url(r'^logout/$', 'logoutUser', name='logoutUser'),

                       url(r'^select/item_id=(?P<item_id>\d+)/(?P<itemtype>\d+)/login/$',
                           'loginUser', name='loginUser'),
                       url(r'^select/item_id=(?P<item_id>\d+)/(?P<itemtype>\d+)/$',
                           'selected', name='selected'),

                       url(r'^editItem/item_id=(?P<item_id>\d+)/login/$',
                           'loginUser', name='loginUser'),
                       url(r'^editItem/item_id=(?P<item_id>\d+)$',
                           'editItem', name='editItem'),

                       url(r'^add/item_id=(?P<item_id>\d+)/(?P<itemtype>\d+)$',
                           'incrementQuantity', name='incrementQuantity'),
                       url(r'^sub/item_id=(?P<item_id>\d+)/(?P<itemtype>\d+)$',
                           'decreaseQuantity', name='decreaseQuantity'),

                       url(r'^deletetItem/item_id=(?P<item_id>\d+)\
                           /(?P<itemtype>\d+)$',
                           'deletetItem', name='deletetItem'),

                       url(r'^checkout/login/$',
                           'loginUser', name='loginUser'),
                       url(r'^checkout/$', 'checkout', name='checkout'),

                       url(r'^cart/login/$', 'loginUser', name='loginUser'),
                       url(r'^cart/$', 'cart', name='cart'),

                       url(r'^order/login/$', 'loginUser', name='loginUser'),
                       url(r'^order/$', 'order', name='order'),

                       url(r'^payment/login/$', 'loginUser', name='loginUser'),
                       url(r'^payment/$', 'payment', name='payment'),

                       url(r'^adreesse/login/$',
                           'loginUser', name='loginUser'),
                       url(r'^adreesse/$', 'adreesse', name='adreesse'),



                       )

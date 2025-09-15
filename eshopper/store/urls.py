from django.urls import path
from .views import Login
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('q', views.q, name='q'),
    path('product/<int:product_id>', views.product, name='product'),
    path('collections/<str:product_type>/', views.collections, name='collections'),
    path('cart', views.cart, name='cart'),
    path('add/<str:title>/<int:id>/<str:price>/<str:img>/<path:return_url>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<str:title>/<int:id>/<str:price>/<str:img>/<path:return_url>/', views.remove_from_cart, name='remove_from_cart'),
    path('login', Login.as_view(), name='login'),
    path('logout', views.logout, name='logout'),
    path('signup', views.signup, name='signup'),
    path('order', views.order, name='order'),
    path('orders', views.orders, name='orders'),
    path('orders/<str:order_id>/', views.orders_details, name='orders_details'),
    path('ordered', views.ordered, name='ordered'),
    path('showcase', views.ordered, name='ordered'),
]
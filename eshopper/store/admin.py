from django.contrib import admin
from .models import Product
from .models import Category
from .models import Customer
from .models import Order
from .models import OrderItem

# Register your models here.
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderItem)
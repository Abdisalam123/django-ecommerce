from django.db import models
from django.utils import timezone
from django.db.models import Q

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50)

    @staticmethod
    def get_all_categories():
        return Category.objects.all()
    
    @staticmethod
    def get_all_category_by_name(name):
        return Category.objects.filter(name=name)
    
    def __str__(self):
        return self.name
    
class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address = models.CharField(max_length=100, null=True)
    phone = models.CharField(max_length=11)
    email = models.EmailField()
    password = models.CharField(max_length=100)

    def register(self):
        self.save()

    @staticmethod
    def get_customer_by_email(email):
        try:
            return Customer.objects.get(email=email)
        except:
            return False
        
    def isExists(self):
        if Customer.objects.filter(email=self.email):
            return True
        
        return False
    
    def __str__(self):
        return self.first_name + ' ' + self.last_name
    
class Product(models.Model):
    title = models.CharField(max_length=60)
    material = models.CharField(max_length=60)
    description = models.CharField(max_length=1000, default='', blank=True, null=True)
    price = models.IntegerField(default=0)
    amount_sold = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    image = models.ImageField(upload_to='store\static')

    @staticmethod
    def search(query):
        return Product.objects.filter(Q(title__icontains=query) | Q(category__name__icontains=query)).values()
    
    @staticmethod
    def get_products_by_id(ids):
        return Product.objects.filter(id__in=ids)
    
    @staticmethod
    def get_all_products():
        return Product.objects.all()
    
    @staticmethod
    def get_all_products_by_category_id(id):
        if id:
            return Product.objects.filter(category=id)
        else:
            return Product.get_all_products()
    
    def __str__(self):
        return self.title
        
class Order(models.Model):
    # This field links an order to a single customer
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    
    # This field creates the many-to-many relationship to Product.
    # It points to the intermediary "through" model.
    products = models.ManyToManyField(Product, through='OrderItem')
    
    address = models.CharField(max_length=50, default='', blank=True)
    phone = models.CharField(max_length=50, default='', blank=True)
    date = models.DateField(default=timezone.now)
    status = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.id)

# This is the new intermediary model.
# Each instance represents a single line item within an order.
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.IntegerField()  # Price at the time of purchase
    
    def __str__(self):
        return f"{self.quantity} x {self.product.title}"
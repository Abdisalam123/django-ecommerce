from .models import Product, Customer, Order, OrderItem
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views import View
import random

def home(request):
    """
    Renders the main index page, populating session data and product lists.
    """
    #Fetch products for home page (Most sold and Hot)
    most_sold_products = Product.objects.all().order_by('-amount_sold').values()[:8]
    hot_products = Product.objects.all().order_by('price').values()[:3]
    #List to hold products
    most_sold_prod = []
    hot_prod = []
    #Iterate and create map for context.
    for product in most_sold_products:
        full_path = product['image']
        index = full_path.rfind('/')
        path = full_path[index+1:]
        most_sold_prod.append({'product': product, 'image_path': {'path': path}})

    for product in hot_products:
        full_path = product['image']
        index = full_path.rfind('/')
        path = full_path[index+1:]
        price_cut = int(product['price'] * 1.6)
        hot_prod.append({'product': product, 'image_path': {'path': path}, 'price_cut': price_cut})

    # Use .get() to retrieve existing session data or initialize with an empty dictionary.
    cust = request.session.get('Customer', {})
    cart = request.session.get('Cart', {})
    
    # Initialize Customer and Cart session.
    if 'First_Name' not in cust:
        cust['First_Name'] = 'Guest'
    
    if 'Session_ID' not in cust:
        cust['Session_ID'] = request.session.session_key
    
    if 'Cart_ID' not in cart:
        cart['Cart_ID'] = str(random.randint(0, 999))
    
    if 'Quantity' not in cart:
        cart['Quantity'] = 0
    
    if 'Products' not in cart:
        cart['Products'] = {}
    
    #Reassign values to session and set session modified to true.
    request.session['Customer'] = cust
    request.session['Cart'] = cart
    request.session.modified = True
    #Context map holding data for home page.
    context = {
        'Customer': cust,
        'Cart': cart,
        'Most_Sold_Products': most_sold_prod,
        'Hot_Products': hot_prod,
    }

    return render(request, 'home.html', context)

def q(request):
    """
    Handles product search functionality.
    """
    cart = request.session.get('Cart', {})
    # Retrieve search term
    search = request.GET.get('search') or request.POST.get('search')
    searchRes = []
    
    if search:
        
        products = Product.search(search)

        for product in products:
            full_path = product['image']
            index = full_path.rfind('/')
            path = full_path[index+1:]
            searchRes.append({'product': product, 'image_path': {'path': path}})

        return render(request, 'q.html', {'Products': searchRes, 'Cart': cart})
    else:
        # Redirect to the home page if no search query is provided.
        return redirect('home')

def product(request, product_id):
    """
    Displays the details of a specific product.
    """
    cart = request.session.get('Cart', {})
    cust = request.session.get('Customer', {})
    
    try:
        product_obj = Product.objects.get(id=product_id)
        full_path = str(product_obj.image)
        index = full_path.rfind('/')
        img = full_path[index+1:]
        context = {
            'product': product_obj,
            'Image': img,
            'Cart': cart,
            'Customer': cust
        }
        return render(request, 'product.html', context)
    except Product.DoesNotExist:
        # Redirect to the home page or a 404 page if the product is not found
        return redirect('home')

def collections(request, product_type):

    cart = request.session.get('Cart', {})
    cust = request.session.get('Customer', {})
    prod = Product.objects.all().filter(category__name=product_type).values()
    collections = [

    ]
    for product in prod:
        full_path = product['image']
        index = full_path.rfind('/')
        path = full_path[index+1:]
        collections.append({'product': product, 'image_path': {'path': path}})

    context = {
        'Products': collections,
        'Name': product_type,
        'Cart': cart,
        'Customer': cust,
    }
    
    return render(request, 'collections.html', context)

class Login(View):
    """
    Renders the login page, it gets user from database and initializes user into customer session.
    """
    def get(self, request):
        cart = request.session.get('Cart', {})
        cust = request.session.get('Customer', {})
        return render(request, 'login.html', {'Cart': cart, 'Customer': cust})

    def post(self, request):
        #Get POST data
        email = request.POST.get('email')
        password = request.POST.get('password')
        customer = Customer.get_customer_by_email(email)
        error_message = None
        #Validate input and store customer session
        if customer:
            if check_password(password, customer.password):
                # Correctly set the customer session data
                request.session['Customer'] = {
                    'First_Name': customer.first_name,
                    'Last_Name': customer.last_name,
                    'ID': customer.id,
                    'Email': customer.email,
                    'Address': customer.address,
                    'Phone': customer.phone
                }
                request.session.modified = True

                return redirect('home')
            else:
                error_message = 'Invalid credentials!'
        else:
            error_message = 'Invalid credentials!'

        cart = request.session.get('Cart', {})
        cust = request.session.get('Customer', {})
        return render(request, 'login.html', {'error': error_message, 'Cart': cart, 'Customer': cust})

def logout(request):
    request.session.clear()
    return redirect('home')

@csrf_protect
def signup(request):
    """
    Saves new customer to database.
    """
    cart = request.session.get('Cart', {})
    cust = request.session.get('Customer', {})

    if request.method == 'POST':
        postData = request.POST
        first_name = postData.get('first_name')
        last_name = postData.get('last_name')
        address = postData.get('address')
        phone = postData.get('phone')
        email = postData.get('email')
        password = postData.get('password')
        
        # validation
        value = {
            'first_name': first_name,
            'last_name': last_name,
            'address': address,
            'phone': phone,
            'email': email
        }
        error_message = None

        customer = Customer(first_name=first_name,
                            last_name=last_name,
                            address=address,
                            phone=phone,
                            email=email,
                            password=password)
        error_message = validateCustomer(customer)

        if not error_message:
            customer.password = make_password(customer.password)
            customer.register()
            return redirect('home')
        else:
            data = {
                'error': error_message,
                'values': value,
                'Cart': cart
            }
            
            return render(request, 'signup.html', data)
        
    return render(request, 'signup.html', {'Cart': cart, 'Customer': cust })

def validateCustomer(customer):
    """
    Validates customer data.
    """
    error_message = None
    if (not customer.first_name):
        error_message = "Please Enter your First Name !!"
    elif len(customer.first_name) < 3:
        error_message = 'First Name must be 3 char long or more'
    elif not customer.last_name:
        error_message = 'Please Enter your Last Name'
    elif len(customer.last_name) < 3:
        error_message = 'Last Name must be 3 char long or more'
    elif not customer.phone:
        error_message = 'Enter your Phone Number'
    elif len(customer.phone) < 10:
        error_message = 'Phone Number must be 10 char Long'
    elif len(customer.password) < 5:
        error_message = 'Password must be 5 char long'
    elif len(customer.email) < 5:
        error_message = 'Email must be 5 char long'
    elif customer.isExists():
        error_message = 'Email Address Already Registered..'

    return error_message

def cart(request):
    """
    Renders the shopping cart page.
    """
    cart = request.session.get('Cart', {})
    cust = request.session.get('Customer', {})

    return render(request,'cart.html', {'Cart': cart, 'Customer': cust})

def add_to_cart(request, title, id, price, img, return_url):
    """
    Adds a product to the cart session and redirects to a specified URL.
    """
    cart = request.session.get('Cart', {})
    price = float(price)
    
    if 'Quantity' not in cart:
        cart['Quantity'] = 0
    if 'Products' not in cart:
        cart['Products'] = {}
    
    product_key = f"{title}_{id}"
    
    if product_key in cart['Products']:
        cart['Products'][product_key]['Quantity'] += 1
    else:
        cart['Products'][product_key] = {
            'title': title,
            'Product_ID': id,
            'Price': price,
            'Quantity': 1,
            'Image': img
        }
    
    total_quantity = 0
    total_price = 0.0
    
    for product_data in cart['Products'].values():
        quantity = product_data['Quantity']
        unit_price = product_data['Price']
        product_data['Product_Total'] = quantity * unit_price
        total_quantity += quantity
        total_price += product_data['Product_Total']
    
    cart['Quantity'] = total_quantity
    cart['Cart_Total'] = round(total_price, 2)
    
    request.session['Cart'] = cart
    request.session.modified = True

    # Redirect to the URL provided in the function call.
    return redirect(return_url)

def remove_from_cart(request, title, id, price, img, return_url):
    """
    Removes a product from the cart session by reducing quantity by 1.
    If quantity reaches 0, removes the product entirely.
    """
    cart = request.session.get('Cart', {})
    
    # Convert price to float
    price = float(price)
    
    # Initialize cart structure if keys are missing
    if 'Quantity' not in cart:
        cart['Quantity'] = 0
    if 'Products' not in cart:
        cart['Products'] = {}
    
    # Create unique key
    product_key = f"{title}_{id}"
    
    if product_key in cart['Products']:
        # Product exists, decrement quantity
        cart['Products'][product_key]['Quantity'] -= 1
        
        # Remove product if quantity reaches 0 or below
        if cart['Products'][product_key]['Quantity'] <= 0:
            del cart['Products'][product_key]
    
    # Calculate totals from scratch
    total_quantity = 0
    total_price = 0.0
    
    for product_data in cart['Products'].values():
        quantity = product_data['Quantity']
        unit_price = product_data['Price']
        
        # Calculate product total
        product_data['Product_Total'] = quantity * unit_price
        
        # Add to cart totals
        total_quantity += quantity
        total_price += product_data['Product_Total']
    
    # Update cart totals
    cart['Quantity'] = total_quantity
    cart['Cart_Total'] = round(total_price, 2)
    
    # Save to session
    request.session['Cart'] = cart
    request.session.modified = True

    # Redirect to the URL provided in the function call.
    return redirect(return_url)

def order(request):
    if request.method == 'POST':
        # Get cart and customer data from session
        cart = request.session.get('Cart', {})
        cust = request.session.get('Customer', {})
        
        # Handle the case where the cart is empty
        if not cart.get('Products'):
            return redirect('home')

        # Determine if the user is logged in
        customer_obj = None
        if 'ID' in cust:
            # User is logged in
            try:
                customer_obj = Customer.objects.get(id=cust['ID'])
            except Customer.DoesNotExist:
                # Handle case where customer is logged in but not found in DB
                return redirect('home')
        else:
            # Guest user, create a temporary customer entry
            try:
                guest_email = request.POST.get('email')
                guest_first_name = request.POST.get('first_name')
                guest_last_name = request.POST.get('last_name')
                address = request.POST.get('address')
                phone = request.POST.get('phone')
                passwordTemp = request.POST.get('password')
                password = make_password(passwordTemp)
                customer_obj, created = Customer.objects.get_or_create(
                    first_name="Customer",
                    email=guest_email,
                    defaults={
                        'first_name': guest_first_name,
                        'last_name': guest_last_name,
                        'address': address, 
                        'phone': phone,
                        'password': password
                    }
                )
            except Exception as e:
                # Handle potential database errors
                return redirect('home')

        # Create the Order object
        order = Order.objects.create(
            customer=customer_obj,
            address=cust.get('Address', ''),  # Assuming address is in session for logged-in users
            phone=cust.get('Phone', ''),      # Assuming phone is in session for logged-in users
        )

        # Prepare order details for email and database
        order_items_data = []
        total_price = 0.0

        # Loop through cart products and create OrderItem entries
        for product_key, item_data in cart['Products'].items():
            try:
                product_obj = Product.objects.get(id=item_data['Product_ID'])
                OrderItem.objects.create(
                    order=order,
                    product=product_obj,
                    quantity=item_data['Quantity'],
                    price=item_data['Price']
                )
                # Update the amount_sold field in the Product model
                product_obj.amount_sold += item_data['Quantity']
                product_obj.save()
                
                # Add item data to a list for the email
                order_items_data.append({
                    'title': item_data['title'],
                    'quantity': item_data['Quantity'],
                    'price': item_data['Price']
                })
                total_price += item_data['Price'] * item_data['Quantity']
            except Product.DoesNotExist:
                # Handle case where a product in the cart no longer exists
                continue

        # Render the HTML template for the email

        html_message = render_to_string('email_confirmation.html', {
            'customer_name': customer_obj.first_name,
            'order_items': order_items_data,
            'total_price': total_price
        })

        # Create a plain-text version for email clients that don't support HTML
        plain_message = strip_tags(html_message)

        # Send the email
        send_mail(
            'Order Confirmation',
            plain_message,
            'Eshopper@example.com',
            [customer_obj.email],
            fail_silently=False,
            html_message=html_message
        )
        
        # Clear the cart from the session after successful order
        del request.session['Cart']
        request.session.modified = True
        
        # Redirect to the order confirmation page
        return redirect('ordered')
    
    # If it's a GET request, just render the order page
    return render(request, 'order.html', {'Cart': request.session.get('Cart', {}), 'Customer': request.session.get('Customer', {})})

def orders(request):
    """
    Displays a list of all orders for the logged-in customer or guest user.
    """
    cust = request.session.get('Customer', {})
    cart = request.session.get('Cart', {})
    if 'ID' in cust:
        # Logged-in customer
        customer_id = cust['ID']
        orders = Order.objects.filter(customer_id=customer_id).order_by('-date')
        return render(request, 'orders.html', {'Orders': orders, 'Cart': cart, 'Customer': cust})
    else:
        # Guest user
        session_key = request.session.session_key
        # Find the temporary guest customer
        try:
            guest_customer = Customer.objects.get(email=f"guest-{session_key}@guest.com")
            orders = Order.objects.filter(customer=guest_customer).order_by('-date')
            return render(request, 'orders.html', {'Orders': orders})
        except Customer.DoesNotExist:
            return render(request, 'orders.html', {'Orders': []})

def orders_details(request, order_id):
    """
    Displays the details of a specific order.
    """
    cust = request.session.get('Customer', {})
    cart = request.session.get('Cart', {})
    
    # Determine the customer object to check ownership
    customer_obj = None
    if 'ID' in cust:
        try:
            customer_obj = Customer.objects.get(id=cust['ID'])
        except Customer.DoesNotExist:
            return redirect('home')
    else:
        try:
            session_key = request.session.session_key
            customer_obj = Customer.objects.get(email=f"guest-{session_key}@guest.com")
        except Customer.DoesNotExist:
            return redirect('home')

    # Get the order and check if it belongs to the current user
    try:
        order = Order.objects.get(id=order_id, customer=customer_obj)
        order_items = OrderItem.objects.filter(order=order)

        sum = 0
        for x in order_items:
            sum += x.price

        return render(request, 'orders_details.html', {'order': order, 'order_items': order_items, 'Cart': cart, 'Customer': cust, 'Sum': sum})
    except Order.DoesNotExist:
        # Redirect if the order does not exist or doesn't belong to the user
        return redirect('home')


def ordered(request):

    cust = request.session.get('Customer', {})
    cart = request.session.get('Cart', {})

    context = {
        'Cart': cart,
        'Customer': cust
    }

    return render(request, 'ordered.html', context)

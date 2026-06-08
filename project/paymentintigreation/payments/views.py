import razorpay
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from .models import Order
from decimal import Decimal

# Predefined premium tiers
PRODUCTS = {
    'basic': {'name': 'Starter Plan', 'price': 299.00, 'features': ['1 Project Dashboard', 'Essential Analytics', 'Email Support']},
    'premium': {'name': 'Growth Plan', 'price': 999.00, 'features': ['10 Project Dashboards', 'Priority Advanced Analytics', '24/7 Priority Support', 'Custom Branding']},
    'enterprise': {'name': 'Scale Plan', 'price': 2999.00, 'features': ['Unlimited Project Dashboards', 'Real-time Analytics API', 'Dedicated Account Manager', 'Custom Integrations']}
}

def checkout(request):
    """
    Renders checkout page. Users can either click a pre-defined product plan
    or type a custom payment amount.
    """
    # Check if user cancelled their payment modal earlier
    status = request.GET.get('status')
    if status == 'cancelled':
        messages.warning(request, "Payment was cancelled. You can try again whenever you are ready.")

    return render(request, 'payments/checkout.html', {
        'products': PRODUCTS,
    })

def initiate_payment(request):
    """
    Creates a Razorpay Order, registers a pending Order in our DB,
    and forwards order details to the loading page for Razorpay Gateway Checkout.
    """
    if request.method == "POST":
        customer_name = request.POST.get('name', '').strip()
        customer_email = request.POST.get('email', '').strip()
        product_key = request.POST.get('product_key', '')
        custom_amount = request.POST.get('custom_amount', '')

        # Basic inputs validation
        if not customer_name or not customer_email:
            messages.error(request, "Please fill in all customer details (Name and Email).")
            return redirect('checkout')

        # Determine price based on selected plan or custom amount
        if product_key in PRODUCTS:
            product = PRODUCTS[product_key]
            amount = Decimal(product['price'])
            description = f"Purchase of {product['name']}"
        else:
            try:
                amount = Decimal(custom_amount)
                if amount <= 0:
                    raise ValueError()
                description = "Custom Donation / Payment"
            except ValueError:
                messages.error(request, "Please select a valid plan or enter a positive custom amount.")
                return redirect('checkout')

        # Convert to Paise for Razorpay
        amount_in_paise = int(amount * 100)

        # Initialize Razorpay SDK Client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        try:
            # Create Razorpay Order
            razorpay_order_data = {
                'amount': amount_in_paise,
                'currency': 'INR',
                'receipt': f"receipt_{customer_name[:10].replace(' ', '_').lower()}",
            }
            razorpay_order = client.order.create(data=razorpay_order_data)
            
            # Save Pending Order in Django Database
            order = Order.objects.create(
                name=customer_name,
                email=customer_email,
                amount=amount,
                razorpay_order_id=razorpay_order['id'],
                status=Order.StatusChoices.PENDING
            )

            # Renders loader that immediately triggers Razorpay's overlay
            return render(request, 'payments/pay.html', {
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'razorpay_order_id': razorpay_order['id'],
                'amount_paise': amount_in_paise,
                'name': customer_name,
                'email': customer_email,
                'description': description,
                'order': order,
            })

        except Exception as e:
            messages.error(request, f"Error initiating payment gateway: {str(e)}")
            return redirect('checkout')

    return redirect('checkout')

def payment_callback(request):
    """
    Handles payment callback from Razorpay Client.
    Validates Razorpay payment signature and updates the DB Order status.
    """
    if request.method == "POST":
        razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
        razorpay_order_id = request.POST.get('razorpay_order_id', '')
        razorpay_signature = request.POST.get('razorpay_signature', '')
        error_reason = request.POST.get('error_reason', '')

        # Locate matching database Order
        try:
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
        except Order.DoesNotExist:
            return render(request, 'payments/status.html', {
                'status': 'error',
                'message': 'We could not locate your transaction order in our database.'
            })

        # Handle UI payment failures reported by Razorpay
        if error_reason:
            order.status = Order.StatusChoices.FAILED
            order.razorpay_payment_id = razorpay_payment_id
            order.save()
            return render(request, 'payments/status.html', {
                'status': 'failed',
                'order': order,
                'error_message': error_reason
            })

        # Initialize Razorpay SDK for Signature Verification
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            # Verify signature using SDK
            client.utility.verify_payment_signature(params_dict)
            
            # If verification succeeded
            order.status = Order.StatusChoices.SUCCESS
            order.razorpay_payment_id = razorpay_payment_id
            order.razorpay_signature = razorpay_signature
            order.save()

            return render(request, 'payments/status.html', {
                'status': 'success',
                'order': order
            })

        except Exception as e:
            # If verification failed
            order.status = Order.StatusChoices.FAILED
            order.razorpay_payment_id = razorpay_payment_id
            order.razorpay_signature = razorpay_signature
            order.save()

            return render(request, 'payments/status.html', {
                'status': 'failed',
                'order': order,
                'error_message': f'Signature verification failed. The payment might be illegitimate. Details: {str(e)}'
            })

    return redirect('checkout')

from django.views.generic import TemplateView, View
from django.http import JsonResponse
from .models import QueryForm, GenericForm, Service, ConsultationForm, Product, Order
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
import razorpay
from django.conf import settings
from django.urls import reverse

class HomePageView(TemplateView): 
    template_name = "home.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['popular_services'] = Service.objects.all()[:4]  # Get 4 services for buttons
        
        # Fetch specific products
        context['consultation_product'] = Product.objects.prefetch_related("fields").filter(name="1-on-1 Consultation with IP Expert").first()
        context['registration_product'] = Product.objects.prefetch_related("fields").filter(name="Expert Assisted Search + Registration").first()

        return context
    
def submit_consultation(request):
    if request.method == "POST":
        try:
            consultation = ConsultationForm(
                name=request.POST.get('name'),
                email=request.POST.get('email'),
                phone_number=request.POST.get('phone_number'),
                date=request.POST.get('date'),
                service=request.POST.get('service'),
                query=request.POST.get('query', ''),
                status='Pending'  # Default status
            )
            consultation.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def search_services(request):
    query = request.GET.get('query', '')
    if query:
        services = Service.objects.filter(heading__icontains=query)[:5]  # Limit to 5 results
        results = [{
            'name': service.heading,
            'url': f"/services/{service.slug}/",
            'form_name': service.form_name
        } for service in services]
    else:
        results = []
    return JsonResponse({'results': results})

class ServicesPageView(TemplateView): 
    template_name = "services/services.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service_slug = self.kwargs.get('slug')  # Assuming you're using slugs in URLs
        service = get_object_or_404(Service, slug=service_slug)  # Add slug field to your Service model
        
        context.update({
            'service': service,
            'fields': service.fields.all(),
            'subcontents': service.subcontents.all().order_by('subcontent_number'),
        })
        return context

class SubmitServiceFormView(View):
    def post(self, request):
        if request.method == "POST":
            try:
                form_data = {
                    'name': request.POST.get('name'),
                    'email': request.POST.get('email'),
                    'phone_number': request.POST.get('phone_number'),
                    'city_pincode': request.POST.get('city_pincode'),
                    'updates_on_whatsapp': request.POST.get('updates_on_whatsapp') == 'on',
                    'service': request.POST.get('service'),
                    # status is left blank as requested
                }
                
                GenericForm.objects.create(**form_data)
                
                return JsonResponse({
                    "message": "Your form has been submitted successfully!"
                }, status=200)
            
            except Exception as e:
                return JsonResponse({
                    "error": f"An error occurred: {str(e)}"
                }, status=400)
        
        return JsonResponse({
            "error": "Invalid request method"
        }, status=400)

def submit_query(request):
    if request.method == "POST":
        name = request.POST.get('name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        query = request.POST.get('query')

        QueryForm.objects.create(name=name, phone_number=phone_number, email=email, query=query)

        return JsonResponse({"message": "Query submitted successfully!"}, status=200)

    return JsonResponse({"error": "Invalid request"}, status=400)

class ProductsPageView(TemplateView):
    template_name = "products/products.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_id = self.kwargs.get('product_id')
        
        # Get the specific product being checked out
        context['consultation_product'] = Product.objects.prefetch_related("fields").get(id=product_id)
        
        # Initialize Razorpay client
        context['razorpay_key_id'] = settings.RAZORPAY_KEY_ID
        context['currency'] = 'INR'
        
        return context

    def post(self, request, *args, **kwargs):
        product_id = self.kwargs.get('product_id')
        product = Product.objects.get(id=product_id)
        
        # Create the order with pending status
        order = Order.objects.create(
            product=product,
            customer_name=request.POST.get('customer_name'),
            customer_email=request.POST.get('customer_email'),
            customer_phone=request.POST.get('customer_phone'),
            base_price=product.base_price,
            final_price=product.base_price,
            status='pending'
        )
        
        # Initialize Razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        # Create Razorpay order
        razorpay_order = client.order.create({
            'amount': int(order.final_price * 100),  # Razorpay expects amount in paise
            'currency': 'INR',
            'receipt': order.order_number,
            'payment_capture': 1  # Auto-capture payment
        })
        
        # Save Razorpay order ID to your order
        order.transaction_id = razorpay_order['id']
        order.save()
        
        # Prepare context for payment page
        context = self.get_context_data()
        context.update({
            'order': order,
            'razorpay_order_id': razorpay_order['id'],
            'amount': order.final_price,
            'callback_url': request.build_absolute_uri(reverse('payment_callback')),
            'customer_name': order.customer_name,
            'customer_email': order.customer_email,
            'customer_phone': order.customer_phone,
        })
        
        return self.render_to_response(context)

class PaymentCallbackView(View):
    def get(self, request):
        # Verify payment signature
        razorpay_payment_id = request.GET.get('razorpay_payment_id')
        razorpay_order_id = request.GET.get('razorpay_order_id')
        razorpay_signature = request.GET.get('razorpay_signature')
        
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        
        try:
            # Verify the payment signature
            client.utility.verify_payment_signature(params_dict)
            
            # Update order status to confirmed
            order = Order.objects.get(transaction_id=razorpay_order_id)
            order.status = 'confirmed'
            order.payment_method = 'razorpay'
            order.save()
            
            return HttpResponse("Payment successful! Order confirmed.")
            
        except razorpay.errors.SignatureVerificationError:
            return HttpResponseBadRequest("Invalid payment signature")
        except Order.DoesNotExist:
            return HttpResponseBadRequest("Order not found")

class AboutPageView(TemplateView): 
    template_name = "fillers/about.html"

class ContactPageView(TemplateView): 
    template_name = "fillers/contact.html"

class ConsultPageView(TemplateView): 
    template_name = "fillers/consult.html"

class FaqPageView(TemplateView): 
    template_name = "fillers/faq.html"

class PrivacyPageView(TemplateView): 
    template_name = "fillers/privacy.html"

class TermsPageView(TemplateView): 
    template_name = "fillers/terms.html"
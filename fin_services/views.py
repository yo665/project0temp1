from django.views.generic import TemplateView, View
from django.http import JsonResponse
from .models import QueryForm, GenericForm, Service, ConsultationForm
from django.shortcuts import get_object_or_404

class HomePageView(TemplateView): 
    template_name = "home.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['popular_services'] = Service.objects.all()[:4]  # Get 4 services for buttons
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


class AboutPageView(TemplateView): 
    template_name = "fillers/about.html"

class ContactPageView(TemplateView): 
    template_name = "fillers/contact.html"

class ConsultPageView(TemplateView): 
    template_name = "fillers/consult.html"

class FaqPageView(TemplateView): 
    template_name = "fillers/faq.html"
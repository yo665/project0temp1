# myapp/context_processors.py
from .models import Service

def services_menu(request):
    return {
        'all_services': Service.objects.all().order_by('heading')
    }
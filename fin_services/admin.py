from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Service, Field, SubContent, SubContentField, GenericForm, QueryForm, ConsultationForm

admin.site.site_header = "Fintrix Administration"
admin.site.site_title = "Fintrix Admin Portal"
admin.site.index_title = "Welcome to Fintrix Admin Panel"

# Define resources for import/export
class ServiceResource(resources.ModelResource):
    class Meta:
        model = Service
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ('slug',)

class QueryFormResource(resources.ModelResource):
    class Meta:
        model = QueryForm
        skip_unchanged = True
        report_skipped = True

class ConsultationFormResource(resources.ModelResource):
    class Meta:
        model = ConsultationForm
        skip_unchanged = True
        report_skipped = True

class GenericFormResource(resources.ModelResource):
    class Meta:
        model = GenericForm
        skip_unchanged = True
        report_skipped = True

class SubContentResource(resources.ModelResource):
    class Meta:
        model = SubContent
        skip_unchanged = True
        report_skipped = True

# Inline admin classes remain the same
class FieldInline(admin.TabularInline):
    model = Field
    extra = 1

class SubContentFieldInline(admin.TabularInline):
    model = SubContentField
    extra = 1

class SubContentInline(admin.TabularInline):
    model = SubContent
    extra = 1

# Updated admin classes with import/export
@admin.register(SubContent)
class SubContentAdmin(ImportExportModelAdmin):
    resource_class = SubContentResource
    list_display = ('subcontent_number', 'heading', 'service')
    inlines = [SubContentFieldInline]

@admin.register(Service)
class ServiceAdmin(ImportExportModelAdmin):
    resource_class = ServiceResource
    list_display = ('heading', 'base_price')
    inlines = [FieldInline, SubContentInline]

@admin.register(QueryForm)
class QueryFormAdmin(ImportExportModelAdmin):
    resource_class = QueryFormResource
    list_display = ('name', 'phone_number', 'email', 'status')
    list_filter = ('status',)
    search_fields = ('name', 'phone_number', 'email')

@admin.register(ConsultationForm)
class ConsultationFormAdmin(ImportExportModelAdmin):
    resource_class = ConsultationFormResource
    list_display = ('name', 'phone_number', 'email', 'date', 'status')
    list_filter = ('status', 'date')
    search_fields = ('name', 'phone_number', 'email')

@admin.register(GenericForm)
class GenericFormAdmin(ImportExportModelAdmin):
    resource_class = GenericFormResource
    list_display = ('name', 'phone_number', 'city_pincode', 'status', 'service')
    list_filter = ('name', 'status', 'service')
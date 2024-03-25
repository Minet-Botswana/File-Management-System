from django.contrib import admin
from .models import Company, Department, Post, DepartmentUser

# Register your models here.

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'company')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'department', 'date_created')
    list_filter = ('department', 'date_created')
    search_fields = ('title', 'description')

@admin.register(DepartmentUser)
class DepartmentUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'get_company')
    list_filter = ('department__company', 'department')

    def get_company(self, obj):
        return obj.department.company
    get_company.short_description = 'Company'

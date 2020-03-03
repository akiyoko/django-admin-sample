from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Department, Employee


class EmployeeInline(admin.StackedInline):
    # ForeignKey を持っている側（多側）のモデルをインラインにする
    model = Employee
    fields = ('username', 'last_name', 'first_name')
    extra = 1


class DepartmentAdmin(admin.ModelAdmin):
    inlines = [
        EmployeeInline,
    ]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, Employee):
                # 初期パスワードをセット
                instance.set_password('pass12345')
        super().save_formset(request, form, formset, change)


admin.site.register(Department, DepartmentAdmin)
admin.site.register(Employee, UserAdmin)

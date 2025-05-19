from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Avg
from django.utils.html import format_html
from .models import Car, ParkingSpot, Payment, News, Vacancy, Review, PromoCode, FAQ, ServiceCategory, Service, Coupon, CompanyInfo
from .forms import EmployeeRegistrationForm


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('mark', 'model', 'license_plate', 'get_owners_count')
    list_filter = ('mark', 'model', 'license_plate',)
    filter_horizontal = ('owners',)
    search_fields = ('mark', 'model', 'license_plate')
    
    def get_owners_count(self, obj):
        return obj.owners.count()
    get_owners_count.short_description = 'Количество владельцев'


@admin.register(ParkingSpot)
class ParkingSpotAdmin(admin.ModelAdmin):
    list_display = ('number', 'price', 'currency', 'is_busy', 'user', 'date_of_rent', 'last_payment_date', 'next_payment_date', 'paid_months', 'get_parked_car')
    list_filter = ('is_busy', 'currency')
    search_fields = ('number', 'user__username')
    readonly_fields = ('get_parked_car',)
    fieldsets = (
        ('Основная информация', {
            'fields': ('number', 'price', 'currency', 'is_busy', 'user', 'date_of_rent')
        }),
        ('Информация об оплате', {
            'fields': ('last_payment_date', 'next_payment_date', 'paid_months')
        }),
    )

    def get_parked_car(self, obj):
        car = getattr(obj, 'parked_car', None)
        if car:
            return f"{car.mark} {car.model} ({car.license_plate})"
        return '-'
    get_parked_car.short_description = 'Машина на месте'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('owner', 'amount', 'is_paid', 'receipt_date', 'repayment_date')
    list_filter = ('is_paid', 'receipt_date', 'repayment_date')
    search_fields = ('owner__username', 'amount')
    date_hierarchy = 'receipt_date'


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'summary', 'published_at', 'is_active')
    search_fields = ('title', 'summary', 'content')
    list_filter = ('is_active',)


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'created_at')
    search_fields = ('user__username', 'text')
    list_filter = ('rating',)


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'is_active', 'start_date', 'end_date')
    search_fields = ('code',)
    list_filter = ('is_active',)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'created_at', 'updated_at')
    search_fields = ('question', 'answer')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('updated_at',)
    fieldsets = (
        ('Основная информация', {
            'fields': ('question', 'answer')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_active')
    search_fields = ('name', 'category__name')
    list_filter = ('is_active', 'category')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_amount', 'is_active', 'start_date', 'end_date')
    search_fields = ('code',)
    list_filter = ('is_active',)


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at', 'updated_at')
    search_fields = ('name', 'history', 'requisites', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'logo', 'history', 'requisites')
        }),
        ('Контактная информация', {
            'fields': ('email', 'phone')
        }),
        ('Время работы', {
            'fields': ('working_hours_weekdays', 'working_hours_weekends')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_staff_status', 'debt', 'account_amount')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'birth_date', 'phone')}),
        ('User roles', {
            'fields': ('is_staff', 'is_superuser'),
            'description': 'is_staff determines if the user is an employee'
        }),
        ('Financial info', {'fields': ('debt', 'account_amount', 'last_payment_date')}),
        ('Permissions', {'fields': ('is_active', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'birth_date', 'phone', 'is_staff'),
        }),
    )
    
    def get_staff_status(self, obj):
        if obj.is_superuser:
            return 'Superuser'
        elif obj.is_staff:
            return 'Employee'
        return 'Client'
    get_staff_status.short_description = 'Role in system'


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

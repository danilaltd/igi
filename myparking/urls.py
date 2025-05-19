from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView
from . import views


urlpatterns = [
     path(r'', views.index, name='index'),
     path('accounts/login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
     path('accounts/logout/', LogoutView.as_view(next_page='index'), name='logout'),
     path('accounts/register/', views.registration_view, name='register'),

     path('parking_list/', views.parking_list, name='parking_list'),
     path('parking-list/', views.parking_list, name='parking-list'),
     path('my_parking_list/', views.my_parking_list, name='my_parking_list'),
     path('parking/<int:park_id>/delete/', views.delete_park, name='delete_park'),
     path('parking/<int:id>/rent/', views.rent_parking, name='rent_parking'),

     path('my_cars/', views.my_cars, name='my_cars'),
     path('car-list/', views.my_cars, name='car-list'),
     path('car/add/', views.add_car, name='add_car'),
     path('car/<int:id>/delete/', views.delete_car, name='delete_car'),
     path('car/<int:id>/edit/', views.edit_car, name='edit_car'),

     # Пути для перехода к списку машин на паркинге (status = add/del)
     path('car_in_park/<int:park_id>/<slug:status>/', views.car_in_park, name='car_in_park'),

     # Пути для перехода к действиям с авто из паркинга ("На паркинг", "С паркинга")
     path('interaction_car_for_parking/<int:car_id>/<int:park_id>/<slug:status>/', views.interaction_car_for_parking, name='interaction_car_for_parking'),

     #  Payments
     path('my-payments/', views.my_payments, name='my_payments'),
     path('payment-list/', views.my_payments, name='payment-list'),
     path('payment/<int:payment_id>/paid/', views.payment_paid, name='payment_paid'),

     path('admin/reports/', views.admin_reports, name='admin_reports'),
     path('account/', views.account_management, name='account_management'),

     # Additional URLs for guest features
     path('get_ip/', views.get_ip, name='get_ip'),
     path('get_fact_about_cats/', views.get_fact_about_cats, name='get_fact_about_cats'),

     # News URLs
     path('news/', views.news_list, name='news-list'),
     path('news/<int:pk>/', views.news_detail, name='news-detail'),

     # Vacancy URLs
     path('vacancies/', views.vacancy_list, name='vacancy-list'),
     path('vacancies/<int:pk>/', views.vacancy_detail, name='vacancy-detail'),

     # Review URLs
     path('reviews/', views.review_list, name='review-list'),
     path('reviews/create/', views.review_create, name='review-create'),
     path('reviews/<int:pk>/', views.review_detail, name='review-detail'),
     path('reviews/<int:pk>/update/', views.review_update, name='review-update'),
     path('reviews/<int:pk>/delete/', views.review_delete, name='review-delete'),

     # PromoCode URLs
     path('promocodes/', views.promo_code_list, name='promocode-list'),
     path('promocodes/<int:pk>/', views.promo_code_detail, name='promocode-detail'),

     # FAQ URLs
     path('faqs/', views.faq_list, name='faq-list'),

     # Services
     path('services/', views.service_list, name='service-list'),
     path('services/<int:pk>/', views.service_detail, name='service-detail'),
     path('services/<int:pk>/apply-promo-code/', views.apply_promo_code, name='service-apply-promo-code'),
     path('services/<int:pk>/apply-coupon/', views.apply_coupon, name='service-apply-coupon'),
     path('services/<int:pk>/order/', views.order_service, name='order-service'),
     path('service-categories/', views.service_category_list, name='service-category-list'),
     path('service-categories/<int:pk>/', views.service_category_detail, name='service-category-detail'),

     # Coupons
     path('coupons/', views.coupon_list, name='coupon-list'),
     path('coupons/<int:pk>/', views.coupon_detail, name='coupon-detail'),
     path('apply-promo-code/', views.apply_promo_code, name='apply-promo-code'),
     path('apply-coupon/', views.apply_coupon, name='apply-coupon'),

     path('policy/', views.policy, name='policy'),
     path('company/', views.company_info, name='company-info'),

     path('client/dashboard/', views.client_dashboard, name='client_dashboard'),
     path('employee/dashboard/', views.employee_dashboard, name='employee_dashboard'),

     path('free-parking/<int:id>/', views.free_parking, name='free_parking'),

     path('set_parking_car/<int:parking_id>/', views.set_parking_car, name='set_parking_car'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from datetime import datetime, timedelta
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, Min, Avg, Max, F
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import numpy as np
import os
import seaborn as sns

import requests
from .forms import *
from .models import *
import logging
import json
from decimal import Decimal
import calendar
import pytz
import decimal
from io import BytesIO
from django.core.paginator import Paginator
from collections import Counter
from datetime import date

# Настройка логгеров
logger = logging.getLogger('myparking')
api_logger = logging.getLogger('myparking.api')
auth_logger = logging.getLogger('myparking.auth')

def generate_parking_chart(busy_spots, free_spots):
    """Generate a pie chart for parking spot occupancy"""
    plt.figure(figsize=(8, 6))
    plt.pie([busy_spots, free_spots], 
            labels=['Занято', 'Свободно'],
            colors=['#dc3545', '#28a745'],
            autopct='%1.1f%%')
    plt.title('Загрузка парковки')
    
    # Save plot to a bytes buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    plt.close()
    
    # Convert to base64 string
    image_png = buffer.getvalue()
    buffer.close()
    return base64.b64encode(image_png).decode('utf-8')

def generate_debt_chart(max_debt, avg_debt, min_debt):
    """Generate a bar chart for debt distribution"""
    plt.figure(figsize=(8, 6))
    plt.bar(['Максимальный долг', 'Средний долг', 'Минимальный долг'],
            [float(max_debt), float(avg_debt), float(min_debt)],
            color=['#dc3545', '#ffc107', '#28a745'])
    plt.title('Распределение долгов')
    plt.ylabel('Сумма (BYN)')
    
    # Save plot to a bytes buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    plt.close()
    
    # Convert to base64 string
    image_png = buffer.getvalue()
    buffer.close()
    return base64.b64encode(image_png).decode('utf-8')

def generate_client_activity_chart(total_clients, active_clients, cars_per_client, parkings_per_client):
    """Generate a line chart for client activity"""
    plt.figure(figsize=(8, 6))
    plt.plot(['Всего клиентов', 'Активных клиентов', 'Среднее кол-во машин', 'Среднее кол-во парковок'],
             [total_clients, active_clients, cars_per_client, parkings_per_client],
             marker='o')
    plt.title('Активность клиентов')
    plt.xticks(rotation=45)
    
    # Save plot to a bytes buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    plt.close()
    
    # Convert to base64 string
    image_png = buffer.getvalue()
    buffer.close()
    return base64.b64encode(image_png).decode('utf-8')

def generate_car_marks_chart(car_marks_data):
    """Generate a pie chart for car marks distribution"""
    plt.figure(figsize=(8, 6))
    marks = [item['mark'] for item in car_marks_data]
    counts = [item['count'] for item in car_marks_data]
    
    plt.pie(counts, labels=marks, autopct='%1.1f%%')
    plt.title('Популярность марок автомобилей')
    
    # Save plot to a bytes buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    plt.close()
    
    # Convert to base64 string
    image_png = buffer.getvalue()
    buffer.close()
    return base64.b64encode(image_png).decode('utf-8')

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def index(request):
    """
    Функция отображения для домашней страницы сайта.
    Показывает последнюю опубликованную новость и информацию о времени.
    """
    latest_news = News.objects.order_by('-published_at').first()
    
    # Получаем текущее время в UTC
    current_time_utc = timezone.now()
    
    # Ищем последнюю дату обновления во всех основных таблицах
    last_updates = []
    
    # Проверяем новости
    if News.objects.exists():
        news_date = News.objects.latest('published_at').published_at
        if news_date:
            last_updates.append(news_date)
    
    # Проверяем парковки
    if ParkingSpot.objects.exists():
        parking_date = ParkingSpot.objects.latest('date_of_rent').date_of_rent
        if parking_date:
            # Преобразуем date в datetime
            last_updates.append(timezone.make_aware(datetime.combine(parking_date, datetime.min.time())))
    
    # Проверяем платежи
    if Payment.objects.exists():
        payment_date = Payment.objects.latest('receipt_date').receipt_date
        if payment_date:
            # Преобразуем date в datetime
            last_updates.append(timezone.make_aware(datetime.combine(payment_date, datetime.min.time())))
    
    # Проверяем последний вход пользователя
    if User.objects.exists():
        user_date = User.objects.latest('last_login').last_login
        if user_date:
            last_updates.append(user_date)
    
    # Берем самую последнюю дату
    last_update_utc = max(last_updates) if last_updates else current_time_utc
    
    # Создаем текстовый календарь
    cal = calendar.TextCalendar()
    calendar_text = cal.formatmonth(current_time_utc.year, current_time_utc.month)
    
    context = {
        'latest_news': latest_news,
        'current_date_utc': current_time_utc,
        'last_update_utc': last_update_utc,
        'calendar_text': calendar_text,
    }
    
    return render(request, 'myparking/index.html', context=context)


def is_employee(user):
    return user.is_staff


def is_client(user):
    return not user.is_staff


@login_required
def client_dashboard(request):
    if not is_client(request.user):
        messages.error(request, 'Access denied. Client access only.')
        return redirect('home')
    
    cars = Car.objects.filter(owners=request.user)
    payments = Payment.objects.filter(car__in=cars)
    
    context = {
        'cars': cars,
        'payments': payments,
        'account_amount': request.user.account_amount
    }
    return render(request, 'myparking/client_dashboard.html', context)


@login_required
@user_passes_test(is_employee)
def employee_dashboard(request):
    cars = Car.objects.all()
    payments = Payment.objects.all()
    clients = User.objects.filter(is_staff=False)
    
    context = {
        'cars': cars,
        'payments': payments,
        'clients': clients
    }
    return render(request, 'myparking/employee_dashboard.html', context)


@login_required
def parking_list(request):
    """
    Функция отображения списка парковок.
    """
    filter_busy = request.GET.get('busy')
    filter_min_price = request.GET.get('min_price')
    filter_max_price = request.GET.get('max_price')

    parkings = ParkingSpot.objects.all()

    if filter_busy == 'busy':
        parkings = parkings.filter(is_busy=True)
    elif filter_busy == 'free':
        parkings = parkings.filter(is_busy=False)

    if filter_min_price:
        parkings = parkings.filter(price__gte=float(filter_min_price))
    if filter_max_price:
        parkings = parkings.filter(price__lte=float(filter_max_price))

    parkings_count = parkings.count()

    return render(
        request,
        'myparking/parking_list.html',
        context={'parkings': parkings, 'parkings_count': parkings_count, },
    )


@login_required
def my_parking_list(request):
    user = request.user
    # Получаем только парковки, где пользователь является владельцем
    parkings = ParkingSpot.objects.filter(user=user)
    parkings_count = parkings.count()

    return render(
        request,
        'myparking/my_parking_list.html',
        context={'parkings': parkings, 'parkings_count': parkings_count},
    )


@login_required
def my_cars(request):
    user = request.user
    cars = user.cars.all()
    cars_count = cars.count()

    return render(
        request,
        'myparking/my_cars.html',
        context={'cars': cars, 'cars_count': cars_count, },
    )


@login_required
def car_in_park(request, park_id, status):
    parking = get_object_or_404(ParkingSpot, id=park_id)

    if status == 'add':
        user_cars = request.user.cars.all()
        parking_cars = parking.cars.all()
        cars_to_add = user_cars.difference(parking_cars)
    if status == 'del':
        cars_to_add = parking.cars.all()

    return render(
        request,
        'myparking/car_list_for_park.html',
        context={'parking': parking, 'cars': cars_to_add,
                 'cars_count': cars_to_add.count(), 'status': status},
    )


@login_required
def interaction_car_for_parking(request, car_id, park_id, status):
    car = get_object_or_404(Car, id=car_id)
    parking = get_object_or_404(ParkingSpot, id=park_id)

    if status == 'add':
        parking.cars.add(car)
        messages.success(request, f'Автомобиль {car} добавлен на парковку {parking}')
    elif status == 'del':
        parking.cars.remove(car)
        messages.success(request, f'Автомобиль {car} удален с парковки {parking}')

    return redirect('car_in_park', park_id=park_id, status='add')


@login_required
def my_payments(request):
    user = request.user
    payments = Payment.objects.filter(owner=user)
    payments_count = payments.count()

    return render(
        request,
        'myparking/my_payments.html',
        context={'payments': payments, 'payments_count': payments_count},
    )


@login_required
def rent_parking(request, id):
    parking = get_object_or_404(ParkingSpot, id=id)
    if request.method == 'POST':
        if not parking.is_busy:
            parking.is_busy = True
            parking.user = request.user
            parking.date_of_rent = timezone.now().date()
            parking.save()
            
            # Создаем только один платеж на текущий месяц
            Payment.objects.create(
                owner=request.user,
                park=parking,
                amount=parking.price,
                receipt_date=timezone.now().date(),
                receipt_time=timezone.now().time()
            )
            
            # Увеличиваем долг пользователя
            user = request.user
            user.debt = user.debt + parking.price
            user.save()
            
            messages.success(request, 'Парковочное место успешно арендовано!')
            return redirect('my_payments')
        else:
            messages.error(request, 'Это парковочное место уже занято!')
            return redirect('parking_list')
    return redirect('parking_list')


@login_required
def free_parking(request, id):
    parking = get_object_or_404(ParkingSpot, id=id)
    
    # Проверяем, что пользователь является владельцем парковки
    if parking.user == request.user:
        # Если есть предоплата (отрицательный долг), удаляем следующий платеж
        if request.user.debt < 0:
            next_payment = Payment.objects.filter(
                owner=request.user,
                park=parking,
                is_paid=False,
                receipt_date=parking.next_payment_date
            ).first()
            if next_payment:
                next_payment.delete()
        
        # Убираем машину с парковочного места, если она там есть
        parked_car = Car.objects.filter(parking_spot=parking).first()
        if parked_car:
            parked_car.parking_spot = None
            parked_car.save()
        
        parking.is_busy = False
        parking.user = None
        parking.date_of_rent = None
        parking.next_payment_date = None
        parking.paid_months = 0
        parking.save()
        messages.success(request, 'Парковочное место успешно освобождено!')
    else:
        messages.error(request, 'Вы не можете освободить чужое парковочное место!')
    
    return redirect('my_parking_list')


@login_required
def payment_paid(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, owner=request.user)
    
    if not payment.is_paid:
        # Проверяем достаточно ли средств
        if request.user.account_amount < payment.amount:
            messages.error(request, f'Недостаточно средств на счете. Требуется: {payment.amount} BYN, Доступно: {request.user.account_amount} BYN')
            return redirect('my_payments')
        
        # Списываем средства
        request.user.account_amount -= payment.amount
        request.user.save()
        
        # Отмечаем платеж как оплаченный
        payment.is_paid = True
        payment.repayment_date = timezone.now().date()
        payment.repayment_time = timezone.now().time()
        payment.save()
        
        # Увеличиваем количество оплаченных месяцев
        parking = payment.park
        parking.paid_months += 1
        parking.last_payment_date = timezone.now().date()
        
        # Вычисляем дату следующего платежа на основе даты текущего платежа
        current_date = payment.receipt_date
        if current_date.month == 12:
            next_payment_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            next_payment_date = current_date.replace(month=current_date.month + 1)
        
        parking.next_payment_date = next_payment_date
        parking.save()
        
        # Обновляем долг пользователя (может быть отрицательным - это предоплата)
        user = request.user
        user.debt = user.debt - payment.amount
        user.save()
        
        # Создаем новый платеж на следующий месяц только если парковка все еще занята этим пользователем
        if parking.is_busy and parking.user == request.user:
            Payment.objects.create(
                owner=request.user,
                park=parking,
                amount=parking.price,
                receipt_date=next_payment_date,
                receipt_time=timezone.now().time()
            )
        
        messages.success(request, 'Платеж успешно оплачен!')
    else:
        messages.warning(request, 'Этот платеж уже оплачен!')
    
    return redirect('my_payments')


@login_required
def account_management(request):
    user = request.user
    if request.method == 'POST':
        try:
            amount = Decimal(str(request.POST.get('amount', '0')))
            # Проверяем, что сумма не превышает максимальное значение для Decimal(10,2)
            if amount > Decimal('99999999.99'):
                messages.error(request, 'Сумма не может превышать 99,999,999.99 BYN')
                return redirect('account_management')
                
            if amount > 0:
                # Получаем текущее значение счета или 0, если оно None
                current_amount = user.account_amount or Decimal('0')
                # Проверяем, не превысит ли новая сумма максимальное значение
                new_amount = current_amount + amount
                if new_amount > Decimal('99999999.99'):
                    messages.error(request, 'Итоговая сумма на счете не может превышать 99,999,999.99 BYN')
                    return redirect('account_management')
                
                # Обновляем значение счета
                user.account_amount = new_amount
                user.save(update_fields=['account_amount'])
                messages.success(request, f'Счет успешно пополнен на {amount} BYN')
            else:
                messages.error(request, 'Сумма пополнения должна быть положительной')
        except (ValueError, TypeError, decimal.InvalidOperation):
            messages.error(request, 'Введите корректную сумму')
    
    context = {
        'account_amount': user.account_amount or Decimal('0'),
        'debt': user.debt or Decimal('0')
    }
    return render(request, 'myparking/account_management.html', context)


@login_required
def admin_reports(request):
    if not request.user.is_staff:
        return redirect('home')
    
    # Получаем все автомобили с несколькими владельцами
    cars_with_multiple_owners = []
    for car in Car.objects.all():
        owners = car.owners.all()
        if owners.count() > 1:
            cars_with_multiple_owners.append({
                'car': car,
                'owners': owners
            })
    
    # Получаем клиентов, отсортированных по балансу
    users_by_balance = User.objects.all().order_by('-account_amount')
    
    # Получаем автомобили по маркам
    cars_by_mark = Car.objects.all()
    
    # Получаем клиента с максимальным долгом и его последний платеж
    client_with_max_debt = User.objects.order_by('-debt').first()
    last_payment_date = None
    if client_with_max_debt:
        last_payment = Payment.objects.filter(owner=client_with_max_debt).order_by('-repayment_date').first()
        if last_payment:
            last_payment_date = last_payment.repayment_date

    # Получаем автомобиль с минимальным долгом за период
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    car_with_min_debt = None
    min_debt = 0
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            car_with_min_debt = Car.objects.annotate(
                total_debt=Sum('payments__amount', filter=Q(payments__receipt_date__range=[start, end]))
            ).order_by('total_debt').first()
            if car_with_min_debt:
                min_debt = car_with_min_debt.total_debt or 0
        except ValueError:
            messages.error(request, 'Неверный формат даты. Используйте формат ГГГГ-ММ-ДД')

    # Получаем общий долг за период
    total_debt = 0
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            payments = Payment.objects.filter(receipt_date__range=[start, end])
            total_debt = sum(payment.amount for payment in payments)
        except ValueError:
            messages.error(request, 'Неверный формат даты. Используйте формат ГГГГ-ММ-ДД')

    # Получаем автомобили по выбранной марке
    car_mark = request.GET.get('car_mark')
    cars_by_selected_mark = []
    if car_mark and car_mark != 'None':
        cars_by_selected_mark = Car.objects.filter(mark__iexact=car_mark).prefetch_related('owners')
    
    # Получаем статистику по долгам
    debt_stats = {
        'max_debt': User.objects.aggregate(Max('debt'))['debt__max'] or 0,
        'min_debt': User.objects.aggregate(Min('debt'))['debt__min'] or 0,
        'avg_debt': User.objects.aggregate(Avg('debt'))['debt__avg'] or 0,
        'total_debt': User.objects.aggregate(Sum('debt'))['debt__sum'] or 0,
        'positive_debt_clients': User.objects.filter(debt__gt=0).count(),
        'negative_debt_clients': User.objects.filter(debt__lt=0).count(),
        'zero_debt_clients': User.objects.filter(debt=0).count(),
        'account_amount_stats': {
            'max': User.objects.aggregate(Max('account_amount'))['account_amount__max'] or 0,
            'min': User.objects.aggregate(Min('account_amount'))['account_amount__min'] or 0,
            'avg': User.objects.aggregate(Avg('account_amount'))['account_amount__avg'] or 0,
            'total': User.objects.aggregate(Sum('account_amount'))['account_amount__sum'] or 0,
            'positive': User.objects.filter(account_amount__gt=0).count(),
            'zero': User.objects.filter(account_amount=0).count(),
        }
    }
    
    # Calculate median and mode for debt
    debts = list(User.objects.values_list('debt', flat=True))
    if debts:
        debts.sort()
        n = len(debts)
        if n % 2 == 0:
            debt_stats['median_debt'] = (debts[n//2 - 1] + debts[n//2]) / 2
        else:
            debt_stats['median_debt'] = debts[n//2]
        
        # Calculate mode
        debt_counter = Counter(debts)
        mode_debt = debt_counter.most_common(1)
        debt_stats['mode_debt'] = mode_debt[0][0] if mode_debt else 0
    else:
        debt_stats['median_debt'] = 0
        debt_stats['mode_debt'] = 0

    # Calculate median and mode for account balance
    balances = list(User.objects.values_list('account_amount', flat=True))
    if balances:
        balances.sort()
        n = len(balances)
        if n % 2 == 0:
            debt_stats['median_balance'] = (balances[n//2 - 1] + balances[n//2]) / 2
        else:
            debt_stats['median_balance'] = balances[n//2]
        
        # Calculate mode for balance
        balance_counter = Counter(balances)
        mode_balance = balance_counter.most_common(1)
        debt_stats['mode_balance'] = mode_balance[0][0] if mode_balance else 0
    else:
        debt_stats['median_balance'] = 0
        debt_stats['mode_balance'] = 0

    # Calculate age statistics
    today = date.today()
    ages = []
    for user in User.objects.filter(is_staff=False):  # Только клиенты, не сотрудники
        if user.birth_date:
            age = today.year - user.birth_date.year - ((today.month, today.day) < (user.birth_date.month, user.birth_date.day))
            ages.append(age)
    
    if ages:
        ages.sort()
        n = len(ages)
        age_stats = {
            'min_age': min(ages),
            'max_age': max(ages),
            'avg_age': sum(ages) / n,
            'median_age': (ages[n//2 - 1] + ages[n//2]) / 2 if n % 2 == 0 else ages[n//2]
        }
    else:
        age_stats = {
            'min_age': 0,
            'max_age': 0,
            'avg_age': 0,
            'median_age': 0
        }
    
    # Получаем статистику парковки
    total_parking_spots = ParkingSpot.objects.count()
    busy_parking_spots = ParkingSpot.objects.filter(is_busy=True).count()
    free_parking_spots = total_parking_spots - busy_parking_spots
    occupancy_rate = (busy_parking_spots / total_parking_spots * 100) if total_parking_spots > 0 else 0
    
    # Создаем график распределения долгов
    plt.figure(figsize=(12, 6))
    plt.bar(['Максимальный', 'Средний', 'Медиана', 'Мода', 'Минимальный'], 
            [debt_stats['max_debt'], debt_stats['avg_debt'], debt_stats['median_debt'], 
             debt_stats['mode_debt'], debt_stats['min_debt']],
            color=['#dc3545', '#ffc107', '#17a2b8', '#28a745', '#007bff'])
    plt.title('Распределение долгов')
    plt.ylabel('Сумма (BYN)')
    plt.xticks(rotation=45)
    
    # Сохраняем график в base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    debt_chart = base64.b64encode(buffer.getvalue()).decode()
    plt.close()

    # Создаем график распределения балансов
    plt.figure(figsize=(12, 6))
    plt.bar(['Максимальный', 'Средний', 'Медиана', 'Мода', 'Минимальный'], 
            [debt_stats['account_amount_stats']['max'], 
             debt_stats['account_amount_stats']['avg'],
             debt_stats['median_balance'],
             debt_stats['mode_balance'],
             debt_stats['account_amount_stats']['min']],
            color=['#28a745', '#ffc107', '#17a2b8', '#007bff', '#dc3545'])
    plt.title('Распределение балансов')
    plt.ylabel('Сумма (BYN)')
    plt.xticks(rotation=45)
    
    # Сохраняем график в base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    balance_chart = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    # Создаем график загрузки парковки
    plt.figure(figsize=(10, 6))
    plt.pie([busy_parking_spots, free_parking_spots], 
            labels=['Занято', 'Свободно'],
            autopct='%1.1f%%')
    plt.title('Загрузка парковки')
    
    # Сохраняем график в base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    parking_chart = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    # Получаем статистику по маркам автомобилей
    car_marks_data = Car.objects.values('mark').annotate(count=Count('id')).order_by('-count')
    
    context = {
        'debt_stats': debt_stats,
        'debt_chart': debt_chart,
        'balance_chart': balance_chart,
        'parking_chart': parking_chart,
        'total_parking_spots': total_parking_spots,
        'busy_parking_spots': busy_parking_spots,
        'free_parking_spots': free_parking_spots,
        'occupancy_rate': round(occupancy_rate, 1),
        'car_marks_data': car_marks_data,
        'cars_with_multiple_owners': cars_with_multiple_owners,
        'users_by_balance': users_by_balance,
        'cars_by_mark': cars_by_mark,
        # Добавляем новые данные
        'client_with_max_debt': client_with_max_debt,
        'last_payment_date': last_payment_date,
        'car_with_min_debt': car_with_min_debt,
        'min_debt': min_debt,
        'total_debt': total_debt,
        'cars_by_selected_mark': cars_by_selected_mark,
        'start_date': start_date,
        'end_date': end_date,
        'car_mark': car_mark,
        'age_stats': age_stats,
    }
    
    return render(request, 'myparking/admin_reports.html', context)


# News views
def news_list(request):
    news_list = News.objects.all().order_by('-published_at')
    return render(request, 'myparking/news_list.html', {'news_list': news_list})


# Vacancy views
def vacancy_list(request):
    vacancy_list = Vacancy.objects.filter(is_active=True)
    return render(request, 'myparking/vacancy_list.html', {'vacancy_list': vacancy_list})


def vacancy_detail(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk)
    return render(request, 'myparking/vacancy_detail.html', {'vacancy': vacancy})


# Review views
def review_list(request):
    review_list = Review.objects.all().order_by('-created_at')
    return render(request, 'myparking/review_list.html', {'review_list': review_list})


# PromoCode views
def promo_code_list(request):
    promo_codes = PromoCode.objects.filter(
        is_active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    )
    return render(request, 'myparking/promo_code_list.html', {'promocode_list': promo_codes})


# Service views
def service_list(request):
    services = Service.objects.filter(is_active=True)
    categories = ServiceCategory.objects.all()
    
    # Apply filters
    category_id = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if category_id:
        services = services.filter(category_id=category_id)
    if min_price:
        services = services.filter(price__gte=float(min_price))
    if max_price:
        services = services.filter(price__lte=float(max_price))
    
    # Add pagination
    paginator = Paginator(services, 9)  # Show 9 services per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'myparking/service_list.html', {
        'services': page_obj,
        'categories': categories,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    })


def service_category_list(request):
    categories = ServiceCategory.objects.all()
    return render(request, 'myparking/service_category_list.html', {'categories': categories})


def service_category_detail(request, pk):
    category = get_object_or_404(ServiceCategory, pk=pk)
    services = Service.objects.filter(category=category, is_active=True)
    return render(request, 'myparking/service_category_detail.html', {
        'category': category,
        'services': services
    })


# Coupon views
def coupon_list(request):
    coupons = Coupon.objects.filter(
        is_active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    )
    return render(request, 'myparking/coupon_list.html', {'coupons': coupons})


def company_info(request):
    company = CompanyInfo.objects.first()
    context = {
        'company_info': company,
        'contact_email': company.email if company else 'support@autocar.by',
        'contact_phone': company.phone if company else '+375 (29) 123-45-67',
        'working_hours_weekdays': company.working_hours_weekdays if company else '8:00 - 20:00',
        'working_hours_weekends': company.working_hours_weekends if company else '9:00 - 18:00'
    }
    return render(request, 'myparking/company_info.html', context)


def policy(request):
    """Представление для страницы политики конфиденциальности."""
    return render(request, 'myparking/policy.html')


# Добавляю недостающие view-функции

def registration_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешно завершена!')
            return redirect('index')
        else:
            for field, errors in form.errors.items():
                field_label = form.fields[field].label
                for error in errors:
                    messages.error(request, f'{field_label}: {error}')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def delete_park(request, park_id):
    parking = get_object_or_404(ParkingSpot, id=park_id)
    if request.user.is_staff:
        parking.delete()
        messages.success(request, 'Парковочное место удалено!')
    else:
        messages.error(request, 'У вас нет прав для удаления парковочного места!')
    return redirect('parking_list')

def add_car(request):
    if request.method == 'POST':
        form = CarForm(request.POST)
        if form.is_valid():
            mark = form.cleaned_data['mark']
            model = form.cleaned_data['model']
            license_plate = form.cleaned_data['license_plate']
            
            # Check if car with these exact specifications already exists
            existing_car = Car.objects.filter(
                mark=mark,
                model=model,
                license_plate=license_plate
            ).first()
            
            if existing_car:
                # If car exists, add current user as owner
                if request.user not in existing_car.owners.all():
                    existing_car.owners.add(request.user)
                    messages.success(request, 'Вы добавлены как владелец существующего автомобиля!')
                else:
                    messages.info(request, 'Вы уже являетесь владельцем этого автомобиля!')
            else:
                # If car doesn't exist, create new car
                car = form.save()
                car.owners.add(request.user)
                messages.success(request, 'Автомобиль успешно добавлен!')
            
            return redirect('my_cars')
    else:
        form = CarForm()
    return render(request, 'myparking/add_car.html', {'form': form})

def delete_car(request, id):
    car = get_object_or_404(Car, id=id)
    if request.user in car.owners.all():
        car.owners.remove(request.user)
        if car.owners.count() == 0:
            car.delete()
        messages.success(request, 'Автомобиль успешно удален!')
    else:
        messages.error(request, 'У вас нет прав для удаления этого автомобиля!')
    return redirect('my_cars')

@login_required
def get_ip(request):
    import requests
    ip = None
    error_message = None
    try:
        ip = requests.get('https://api.ipify.org', timeout=5).text
        api_logger.info(f"Successfully retrieved IP: {ip}")
    except Exception as e:
        import traceback
        error_message = f'Ошибка при определении внешнего IP: {e}'
        api_logger.error(f"Error getting IP: {str(e)}\n{traceback.format_exc()}")
    return render(request, 'myparking/get_ip.html', {'ip': ip, 'error_message': error_message})

@login_required
def get_fact_about_cats(request):
    import requests
    fact = None
    error_message = None
    try:
        response = requests.get('https://catfact.ninja/fact', timeout=5)
        if response.status_code == 200:
            data = response.json()
            fact = data.get('fact')
            api_logger.info(f"Successfully retrieved cat fact: {fact}")
        else:
            error_message = 'Не удалось получить факт о котах.'
            api_logger.error(f"Failed to get cat fact. Status code: {response.status_code}")
    except Exception as e:
        import traceback
        error_message = f'Ошибка при получении факта: {e}'
        api_logger.error(f"Error getting cat fact: {str(e)}\n{traceback.format_exc()}")
    return render(request, 'myparking/get_fact_about_cats.html', {'fact': fact, 'error_message': error_message})

def news_detail(request, pk):
    news = get_object_or_404(News, pk=pk)
    return render(request, 'myparking/news_detail.html', {'news': news})

def review_create(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            messages.success(request, 'Отзыв успешно создан!')
            return redirect('review-list')
    else:
        form = ReviewForm()
    return render(request, 'myparking/review_form.html', {'form': form})

def review_detail(request, pk):
    review = get_object_or_404(Review, pk=pk)
    return render(request, 'myparking/review_detail.html', {'review': review})

def review_update(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.user != review.user:
        messages.error(request, 'У вас нет прав для редактирования этого отзыва!')
        return redirect('review-list')
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Отзыв успешно обновлен!')
            return redirect('review-list')
    else:
        form = ReviewForm(instance=review)
    return render(request, 'myparking/review_form.html', {'form': form})

def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.user != review.user:
        messages.error(request, 'У вас нет прав для удаления этого отзыва!')
        return redirect('review-list')
    review.delete()
    messages.success(request, 'Отзыв успешно удален!')
    return redirect('review-list')

def promo_code_detail(request, pk):
    promo_code = get_object_or_404(PromoCode, pk=pk)
    return render(request, 'myparking/promo_code_detail.html', {'promo_code': promo_code})

def faq_list(request):
    faq_list = FAQ.objects.all()
    return render(request, 'myparking/faq_list.html', {'faq_list': faq_list})

def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk)
    applied_promo_code = request.session.get('applied_promo_code')
    applied_coupon = request.session.get('applied_coupon')
    discounted_price = service.price

    if applied_promo_code:
        try:
            promo_code = PromoCode.objects.get(code=applied_promo_code)
            if promo_code.is_valid():
                discount = (service.price * promo_code.discount_percent) / 100
                discounted_price = service.price - discount
            else:
                del request.session['applied_promo_code']
                applied_promo_code = None
        except PromoCode.DoesNotExist:
            del request.session['applied_promo_code']
            applied_promo_code = None

    if applied_coupon:
        try:
            coupon = Coupon.objects.get(code=applied_coupon)
            if coupon.is_valid():
                discounted_price = max(0, service.price - coupon.discount_amount)
            else:
                del request.session['applied_coupon']
                applied_coupon = None
        except Coupon.DoesNotExist:
            del request.session['applied_coupon']
            applied_coupon = None

    context = {
        'service': service,
        'applied_promo_code': applied_promo_code,
        'applied_coupon': applied_coupon,
        'discounted_price': discounted_price,
    }
    return render(request, 'myparking/service_detail.html', context)

def apply_promo_code(request, pk=None):
    if request.method == 'POST':
        code = request.POST.get('code')
        try:
            promo_code = PromoCode.objects.get(code=code)
            if promo_code.is_valid():
                request.session['applied_promo_code'] = code
                messages.success(request, f'Промокод {code} успешно применен!')
            else:
                messages.error(request, 'Промокод недействителен!')
        except PromoCode.DoesNotExist:
            messages.error(request, 'Промокод не найден!')
    
    if pk:
        return redirect('service-detail', pk=pk)
    return redirect('promocode-list')

def apply_coupon(request, pk=None):
    if request.method == 'POST':
        code = request.POST.get('code')
        try:
            coupon = Coupon.objects.get(code=code)
            if coupon.is_valid():
                request.session['applied_coupon'] = code
                messages.success(request, f'Купон {code} успешно применен!')
            else:
                messages.error(request, 'Купон недействителен!')
        except Coupon.DoesNotExist:
            messages.error(request, 'Купон не найден!')
    
    if pk:
        return redirect('service-detail', pk=pk)
    return redirect('coupon-list')

@login_required
def order_service(request, pk):
    if request.method == 'POST':
        service = get_object_or_404(Service, pk=pk)
        price = service.price
        applied_promo_code = request.session.get('applied_promo_code')
        applied_coupon = request.session.get('applied_coupon')

        # Calculate final price with discounts
        if applied_promo_code:
            try:
                promo_code = PromoCode.objects.get(code=applied_promo_code)
                if promo_code.is_valid():
                    discount = (price * promo_code.discount_percent) / 100
                    price = price - discount
            except PromoCode.DoesNotExist:
                pass

        if applied_coupon:
            try:
                coupon = Coupon.objects.get(code=applied_coupon)
                if coupon.is_valid():
                    price = max(0, price - coupon.discount_amount)
                else:
                    pass
            except Coupon.DoesNotExist:
                pass

        # Check if user has enough balance
        if request.user.account_amount >= price:
            # Create payment record
            payment = Payment.objects.create(
                owner=request.user,
                amount=price,
                receipt_date=timezone.now().date(),
                receipt_time=timezone.now().time(),
                is_paid=True,
                repayment_date=timezone.now().date(),
                repayment_time=timezone.now().time()
            )

            # Deduct amount from user's account
            request.user.account_amount -= price
            request.user.save()

            # Clear applied discounts
            if 'applied_promo_code' in request.session:
                del request.session['applied_promo_code']
            if 'applied_coupon' in request.session:
                del request.session['applied_coupon']

            messages.success(request, 'Услуга успешно заказана!')
        else:
            messages.error(request, 'Недостаточно средств на счете!')

    return redirect('service-detail', pk=pk)

def coupon_detail(request, pk):
    coupon = get_object_or_404(Coupon, pk=pk)
    return render(request, 'myparking/coupon_detail.html', {'coupon': coupon})

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.user.is_staff:
        # Статистика для сотрудников
        total_clients = User.objects.filter(is_staff=False).count()
        active_clients = User.objects.filter(is_staff=False, cars__isnull=False).distinct().count()
        clients_with_parkings = User.objects.filter(is_staff=False, parkings__isnull=False).distinct().count()
        
        context = {
            'total_clients': total_clients,
            'active_clients': active_clients,
            'clients_with_parkings': clients_with_parkings,
            'debt_stats': {
                'max_debt': User.objects.filter(is_staff=False).aggregate(max_debt=Max('debt'))['max_debt'] or 0,
                'min_debt': User.objects.filter(is_staff=False).aggregate(min_debt=Min('debt'))['min_debt'] or 0,
                'avg_debt': User.objects.filter(is_staff=False).aggregate(avg_debt=Avg('debt'))['avg_debt'] or 0,
                'total_debt': User.objects.filter(is_staff=False).aggregate(total_debt=Sum('debt'))['total_debt'] or 0,
                'positive_debt_clients': User.objects.filter(is_staff=False, debt__gt=0).count(),
                'negative_debt_clients': User.objects.filter(is_staff=False, debt__lt=0).count(),
                'zero_debt_clients': User.objects.filter(is_staff=False, debt=0).count(),
            },
            'account_stats': {
                'max': User.objects.filter(is_staff=False, account_amount__gt=0).aggregate(max_amount=Max('account_amount'))['max_amount'] or 0,
                'min': User.objects.filter(is_staff=False, account_amount__gt=0).aggregate(min_amount=Min('account_amount'))['min_amount'] or 0,
                'avg': User.objects.filter(is_staff=False, account_amount__gt=0).aggregate(avg_amount=Avg('account_amount'))['avg_amount'] or 0,
                'total': User.objects.filter(is_staff=False, account_amount__gt=0).aggregate(total_amount=Sum('account_amount'))['total_amount'] or 0,
                'positive': User.objects.filter(is_staff=False, account_amount__gt=0).count(),
                'zero': User.objects.filter(is_staff=False, account_amount=0).count(),
            }
        }
    else:
        # Статистика для клиентов
        context = {
            'cars': request.user.cars.all(),
            'parkings': request.user.parkings.all(),
            'payments': request.user.payments.all(),
        }
    
    return render(request, 'myparking/dashboard.html', context)

def edit_car(request, id):
    car = get_object_or_404(Car, id=id)
    
    # Проверяем, является ли пользователь владельцем машины
    if request.user not in car.owners.all():
        messages.error(request, 'У вас нет прав для редактирования этого автомобиля!')
        return redirect('my_cars')
    
    if request.method == 'POST':
        form = CarForm(request.POST, instance=car)
        if form.is_valid():
            # Проверяем, не существует ли уже машина с такими параметрами
            mark = form.cleaned_data['mark']
            model = form.cleaned_data['model']
            license_plate = form.cleaned_data['license_plate']
            
            existing_car = Car.objects.filter(
                mark=mark,
                model=model,
                license_plate=license_plate
            ).exclude(id=car.id).first()
            
            if existing_car:
                messages.error(request, 'Автомобиль с такими параметрами уже существует!')
            else:
                form.save()
                messages.success(request, 'Параметры автомобиля успешно обновлены!')
                return redirect('my_cars')
    else:
        form = CarForm(instance=car)
    
    return render(request, 'myparking/edit_car.html', {'form': form, 'car': car})

@login_required
def set_parking_car(request, parking_id):
    parking = get_object_or_404(ParkingSpot, id=parking_id)
    if parking.user != request.user:
        messages.error(request, 'Вы не владелец этого парковочного места!')
        return redirect('my_parking_list')

    if request.method == 'POST':
        if 'remove_car' in request.POST:
            # Убрать машину с места
            car = getattr(parking, 'parked_car', None)
            if car and car.owners.filter(id=request.user.id).exists():
                car.parking_spot = None
                car.save()
                messages.success(request, 'Машина убрана с парковочного места!')
            else:
                messages.error(request, 'Вы не можете убрать чужую машину!')
            return redirect('my_parking_list')
        else:
            form = CarSelectForm(request.POST, user=request.user)
            if form.is_valid():
                car = form.cleaned_data['car']
                # Проверка: машина не стоит на другом месте
                if car.parking_spot is not None:
                    messages.error(request, 'Машина уже стоит на другом месте!')
                else:
                    car.parking_spot = parking
                    car.save()
                    messages.success(request, 'Машина успешно поставлена на парковку!')
                return redirect('my_parking_list')
    else:
        form = CarSelectForm(user=request.user)
    return render(request, 'myparking/set_parking_car.html', {'parking': parking, 'form': form})

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone
from datetime import timedelta, date
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver


def validate_age_18(value):
    today = timezone.now().date()
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    if age < 18:
        raise ValidationError('Возраст должен быть не менее 18 лет')


def validate_phone_number(value):
    if not value.startswith('375'):
        raise ValidationError('Телефон должен начинаться с 375')
    operator_code = value[3:5]
    if operator_code not in ['29', '33', '44', '25']:
        raise ValidationError('Неверный код оператора. Допустимые коды: 29, 33, 44, 25')
    if not value[5:].isdigit() or len(value[5:]) != 7:
        raise ValidationError('После кода оператора должно быть 7 цифр')


# Расширяем модель User
User.add_to_class('phone', models.CharField(
    max_length=20,
    validators=[validate_phone_number],
    null=True,
    blank=True
))

User.add_to_class('birth_date', models.DateField(
    validators=[validate_age_18],
    null=True,
    blank=True
))

# Поля для клиентов
User.add_to_class('last_payment_date', models.DateField(null=True, blank=True))
User.add_to_class('debt', models.DecimalField(max_digits=10, decimal_places=2, default=0))

# Поля для аккаунта
User.add_to_class('account_amount', models.DecimalField(max_digits=10, decimal_places=2, default=0))
User.add_to_class('account_created_at', models.DateTimeField(default=timezone.now))
User.add_to_class('account_updated_at', models.DateTimeField(default=timezone.now))

# Общие поля
User.add_to_class('created_at', models.DateTimeField(default=timezone.now))
User.add_to_class('updated_at', models.DateTimeField(default=timezone.now))


class Car(models.Model):
    owners = models.ManyToManyField(User, related_name='cars')
    mark = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    license_plate = models.CharField(max_length=20)
    parking_spot = models.OneToOneField('ParkingSpot', on_delete=models.SET_NULL, null=True, blank=True, related_name='parked_car')

    def __str__(self):
        return f"{self.mark} {self.model} ({self.license_plate})"

    def save(self, *args, **kwargs):
        # Если машина уже припаркована на другом месте, убираем её оттуда
        if self.parking_spot:
            old_spot = ParkingSpot.objects.filter(parked_car=self).exclude(id=self.parking_spot.id).first()
            if old_spot:
                old_spot.parked_car = None
                old_spot.save()
        super().save(*args, **kwargs)


class ParkingSpot(models.Model):
    number = models.PositiveIntegerField(unique=True, validators=[MaxValueValidator(999)], help_text="Parking spot number (max 999)")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='BYN', choices=[('BYN', 'BYN'), ('USD', 'USD')])
    is_busy = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='parkings', blank=True, null=True)
    date_of_rent = models.DateField(blank=True, null=True)
    last_payment_date = models.DateField(blank=True, null=True, help_text="Last payment date")
    next_payment_date = models.DateField(blank=True, null=True, help_text="Next payment date")
    paid_months = models.PositiveIntegerField(default=0, help_text="Number of paid months")

    class Meta:
        verbose_name = "Parking Spot"
        verbose_name_plural = "Parking Spots"
        ordering = ['number']

    def __str__(self):
        return f"Parking Spot #{self.number}"

    def save(self, *args, **kwargs):
        if not self.next_payment_date and self.date_of_rent:
            # Устанавливаем дату следующей оплаты через месяц после аренды
            self.next_payment_date = self.date_of_rent + timedelta(days=30)
        super().save(*args, **kwargs)


class Payment(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    park = models.ForeignKey(ParkingSpot, on_delete=models.CASCADE, related_name='payments', blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='BYN', choices=[('BYN', 'BYN'), ('USD', 'Доллар США')])
    is_paid = models.BooleanField(default=False)
    # Дата начисления
    receipt_date = models.DateField(blank=True, null=True)
    receipt_time = models.TimeField(blank=True, null=True)
    # Дата погашения платежа
    repayment_date = models.DateField(blank=True, null=True)
    repayment_time = models.TimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.id} - {self.owner.username}"

    def save(self, *args, **kwargs):
        # Убираем автоматическое увеличение долга
        super().save(*args, **kwargs)


class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    summary = models.TextField(blank=True, help_text="News summary")
    image = models.ImageField(upload_to='news/', null=True, blank=True)
    published_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'News'
        verbose_name_plural = 'News'


class PromoCode(models.Model):
    """Promo code"""
    code = models.CharField(max_length=20, unique=True, verbose_name="Code")
    description = models.TextField(verbose_name="Description")
    discount_percent = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Discount percent",
        default=0
    )
    start_date = models.DateTimeField(verbose_name="Start date", default=timezone.now)
    end_date = models.DateTimeField(verbose_name="End date", default=timezone.now)
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Promo Code"
        verbose_name_plural = "Promo Codes"
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.code} ({self.discount_percent}%)"

    def is_valid(self):
        """Проверка валидности промокода"""
        now = timezone.now()
        return (
            self.is_active and
            self.start_date <= now <= self.end_date
        )


class FAQ(models.Model):
    question = models.CharField(max_length=300, verbose_name="Question")
    answer = models.TextField(verbose_name="Answer")
    created_at = models.DateTimeField(verbose_name="Created at", null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.question


class ServiceCategory(models.Model):
    """Service category"""
    name = models.CharField(max_length=100, verbose_name="Category name")
    description = models.TextField(verbose_name="Category description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Service Category"
        verbose_name_plural = "Service Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Service(models.Model):
    """Service"""
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100, verbose_name="Service name")
    description = models.TextField(verbose_name="Service description")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price")
    currency = models.CharField(max_length=3, default='BYN', choices=[('BYN', 'BYN'), ('USD', 'USD')], verbose_name="Currency")
    duration = models.DurationField(verbose_name="Service duration")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class Coupon(models.Model):
    """Coupon"""
    code = models.CharField(max_length=20, unique=True, verbose_name="Code")
    description = models.TextField(verbose_name="Description")
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Discount amount",
        default=0
    )
    currency = models.CharField(max_length=3, default='BYN', choices=[('BYN', 'BYN'), ('USD', 'USD')], verbose_name="Currency")
    start_date = models.DateTimeField(verbose_name="Start date", default=timezone.now)
    end_date = models.DateTimeField(verbose_name="End date", default=timezone.now)
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.code} ({self.discount_amount})"

    def is_valid(self):
        """Проверка валидности купона"""
        now = timezone.now()
        return (
            self.is_active and
            self.start_date <= now <= self.end_date
        )


class CompanyInfo(models.Model):
    name = models.CharField(max_length=100, verbose_name="Company name")
    logo = models.ImageField(upload_to='company/', null=True, blank=True, verbose_name="Logo")
    history = models.TextField(verbose_name="Company history")
    requisites = models.TextField(verbose_name="Requisites")
    email = models.EmailField(verbose_name="Support email", default="support@autocar.by")
    phone = models.CharField(max_length=20, verbose_name="Contact phone", default="+375 (29) 123-45-67")
    working_hours_weekdays = models.CharField(max_length=50, verbose_name="Working hours (Mon-Fri)", default="8:00 - 20:00")
    working_hours_weekends = models.CharField(max_length=50, verbose_name="Working hours (Sat-Sun)", default="9:00 - 18:00")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Company Info"
        verbose_name_plural = "Company Info"

    def __str__(self):
        return self.name


class Vacancy(models.Model):
    title = models.CharField(max_length=100, verbose_name="Vacancy title")
    description = models.TextField(verbose_name="Description")
    requirements = models.TextField(verbose_name="Requirements", blank=True, null=True)
    salary = models.CharField(max_length=50, verbose_name="Salary", blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Vacancy"
        verbose_name_plural = "Vacancies"

    def __str__(self):
        return self.title


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.rating})"

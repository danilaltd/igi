from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from datetime import date
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import *


class UserRegistrationForm(UserCreationForm):
    phone = forms.CharField(
        required=True,
        label='Телефон',
        help_text='Формат: +375291234567 (375 + код оператора + номер). Коды операторов: 29, 33, 44, 25',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+375291234567'})
    )
    birth_date = forms.DateField(
        required=True,
        label='Дата рождения',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        help_text='Вам должно быть не менее 18 лет'
    )
    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@mail.com'})
    )
    first_name = forms.CharField(
        required=True,
        max_length=30,
        label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иван'})
    )
    last_name = forms.CharField(
        required=True,
        max_length=30,
        label='Фамилия',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иванов'})
    )
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'username'}),
        label='Имя пользователя'
    )
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(),
        label='Пароль'
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(),
        label='Подтверждение пароля'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'birth_date', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ivanov'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.startswith('+375'):
            raise forms.ValidationError('Телефон должен начинаться с +375')
        operator_code = phone[4:6]
        if operator_code not in ['29', '33', '44', '25']:
            raise forms.ValidationError('Неверный код оператора. Допустимые коды: 29, 33, 44, 25')
        if not phone[6:].isdigit() or len(phone[6:]) != 7:
            raise forms.ValidationError('После кода оператора должно быть 7 цифр')
        return phone[1:]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Этот email уже зарегистрирован')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 3:
            raise forms.ValidationError('Имя пользователя должно содержать не менее 3 символов')
        if not username.isalnum():
            raise forms.ValidationError('Имя пользователя должно содержать только буквы и цифры')
        return username

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            today = timezone.now().date()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            if age < 18:
                raise forms.ValidationError('Возраст должен быть не менее 18 лет')
            if birth_date > today:
                raise forms.ValidationError('Дата рождения не может быть в будущем')
        return birth_date

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        user.birth_date = self.cleaned_data['birth_date']
        if commit:
            user.save()
        return user


class EmployeeRegistrationForm(UserRegistrationForm):
    position = forms.CharField(max_length=100, required=True)
    bio = forms.CharField(widget=forms.Textarea, required=False)

    class Meta(UserRegistrationForm.Meta):
        fields = UserRegistrationForm.Meta.fields + ('position', 'bio')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True  # Устанавливаем флаг сотрудника
        user.position = self.cleaned_data['position']
        user.bio = self.cleaned_data['bio']
        
        if commit:
            user.save()
        return user


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['mark', 'model', 'license_plate']


class CarSelectForm(forms.Form):
    car = forms.ModelChoiceField(
        queryset=None,
        label='Выберите автомобиль',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['car'].queryset = Car.objects.filter(owners=user, parking_spot__isnull=True)


class ParkingSpotForm(forms.ModelForm):
    class Meta:
        model = ParkingSpot
        fields = ['number', 'price', 'currency']


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'currency', 'is_paid', 'receipt_date', 'receipt_time', 'repayment_date', 'repayment_time']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']


class PromoCodeForm(forms.ModelForm):
    class Meta:
        model = PromoCode
        fields = ['code', 'description', 'discount_percent', 'start_date', 'end_date', 'is_active']


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'description', 'discount_amount', 'currency', 'start_date', 'end_date', 'is_active']
        widgets = {
            'valid_from': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'valid_to': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'currency', 'duration', 'is_active']


class ServiceCategoryForm(forms.ModelForm):
    class Meta:
        model = ServiceCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

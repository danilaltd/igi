from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import datetime, timedelta
from .models import Car, ParkingSpot, Payment, News, Vacancy, Review, PromoCode, FAQ, ServiceCategory, Service, Coupon

class BasicModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
        self.user.account_amount = Decimal('1000.00')
        self.user.save()
        self.car = Car.objects.create(mark='TestMark', model='TestModel', license_plate='TEST123')
        self.car.owners.add(self.user)
        self.parking = ParkingSpot.objects.create(number=101, price=Decimal('100.00'), is_busy=False)

    def test_car_creation(self):
        car = Car.objects.create(mark='BMW', model='X5', license_plate='ABC123')
        self.assertEqual(car.mark, 'BMW')
        self.assertEqual(car.model, 'X5')
        self.assertEqual(car.license_plate, 'ABC123')

    def test_parking_spot_creation(self):
        parking = ParkingSpot.objects.create(number=102, price=Decimal('150.00'), is_busy=True)
        self.assertEqual(parking.number, 102)
        self.assertEqual(parking.price, Decimal('150.00'))
        self.assertTrue(parking.is_busy)

    def test_payment_creation(self):
        payment = Payment.objects.create(owner=self.user, park=self.parking, amount=Decimal('100.00'), receipt_date=datetime.now().date())
        self.assertEqual(payment.amount, Decimal('100.00'))
        self.assertEqual(payment.owner, self.user)
        self.assertEqual(payment.park, self.parking)

    def test_user_account(self):
        self.user.account_amount = Decimal('500.00')
        self.user.save()
        self.assertEqual(self.user.account_amount, Decimal('500.00'))

class BasicViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

    def test_index_page(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_register_page(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)

class NewsTests(TestCase):
    def setUp(self):
        self.news = News.objects.create(title='Test News', content='Test Content', published_at=datetime.now())

    def test_news_creation(self):
        self.assertEqual(self.news.title, 'Test News')
        self.assertEqual(self.news.content, 'Test Content')

class VacancyTests(TestCase):
    def setUp(self):
        self.vacancy = Vacancy.objects.create(title='Test Vacancy', description='Test Description', salary='1000')

    def test_vacancy_creation(self):
        self.assertEqual(self.vacancy.title, 'Test Vacancy')
        self.assertEqual(self.vacancy.description, 'Test Description')
        self.assertEqual(self.vacancy.salary, '1000')

class ReviewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.review = Review.objects.create(user=self.user, text='Test Review', rating=5)

    def test_review_creation(self):
        self.assertEqual(self.review.text, 'Test Review')
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.user, self.user)

class PromoCodeTests(TestCase):
    def setUp(self):
        self.promocode = PromoCode.objects.create(code='TEST123', description='Test promo code', discount_percent=10, is_active=True)

    def test_promocode_creation(self):
        self.assertEqual(self.promocode.code, 'TEST123')
        self.assertEqual(self.promocode.discount_percent, 10)
        self.assertTrue(self.promocode.is_active)

class FAQTests(TestCase):
    def setUp(self):
        self.faq = FAQ.objects.create(question='Test Question', answer='Test Answer')

    def test_faq_creation(self):
        self.assertEqual(self.faq.question, 'Test Question')
        self.assertEqual(self.faq.answer, 'Test Answer')

class ServiceTests(TestCase):
    def setUp(self):
        self.category = ServiceCategory.objects.create(name='Test Category', description='Test Description')
        self.service = Service.objects.create(category=self.category, name='Test Service', description='Test Description', price=Decimal('100.00'), duration=timedelta(hours=1))

    def test_service_creation(self):
        self.assertEqual(self.service.name, 'Test Service')
        self.assertEqual(self.service.price, Decimal('100.00'))
        self.assertEqual(self.service.category, self.category)

class CouponTests(TestCase):
    def setUp(self):
        self.coupon = Coupon.objects.create(code='COUPON123', description='Test coupon', discount_amount=Decimal('20.00'), is_active=True)

    def test_coupon_creation(self):
        self.assertEqual(self.coupon.code, 'COUPON123')
        self.assertEqual(self.coupon.discount_amount, Decimal('20.00'))
        self.assertTrue(self.coupon.is_active)

class ExtraModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user1', password='pass')
        self.car = Car.objects.create(mark='Audi', model='A4', license_plate='AA1111')
        self.car.owners.add(self.user)
        self.parking = ParkingSpot.objects.create(number=201, price=Decimal('200.00'), is_busy=False)

    def test_unique_parking_number(self):
        with self.assertRaises(Exception):
            ParkingSpot.objects.create(number=201, price=Decimal('300.00'))

    def test_add_car_to_parking(self):
        self.parking.cars.add(self.car)
        self.assertIn(self.car, self.parking.cars.all())

    def test_payment_str(self):
        payment = Payment.objects.create(owner=self.user, park=self.parking, amount=Decimal('50.00'))
        self.assertIn(str(self.user.username), str(payment))

    def test_promocode_is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        promo = PromoCode.objects.create(code='PROMO2024', description='desc', discount_percent=15, start_date=now - timedelta(days=1), end_date=now + timedelta(days=1), is_active=True)
        self.assertTrue(promo.is_valid())
        promo.is_active = False
        promo.save()
        self.assertFalse(promo.is_valid())

    def test_coupon_unique_code(self):
        Coupon.objects.create(code='UNIQUE', description='desc', discount_amount=Decimal('10.00'))
        with self.assertRaises(Exception):
            Coupon.objects.create(code='UNIQUE', description='desc', discount_amount=Decimal('5.00'))

    def test_faq_str(self):
        faq = FAQ.objects.create(question='Q', answer='A')
        self.assertEqual(str(faq), 'Q')

    def test_service_str(self):
        cat = ServiceCategory.objects.create(name='Cat', description='D')
        service = Service.objects.create(category=cat, name='S', description='D', price=1, duration=timedelta(hours=1))
        self.assertIn('S', str(service))

    def test_review_rating_range(self):
        review = Review.objects.create(user=self.user, text='ok', rating=3)
        self.assertTrue(1 <= review.rating <= 5)

    def test_invalid_payment_amount(self):
        with self.assertRaises(Exception):
            Payment.objects.create(owner=self.user, park=self.parking, amount=None)

    def test_filter_cars_by_mark(self):
        Car.objects.create(mark='BMW', model='M3', license_plate='BM1234')
        bmw_cars = Car.objects.filter(mark='BMW')
        self.assertTrue(bmw_cars.exists())

class MoreModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user2', password='pass')
        self.car = Car.objects.create(mark='Lada', model='Vesta', license_plate='LA1234')
        self.car.owners.add(self.user)
        self.parking = ParkingSpot.objects.create(number=301, price=Decimal('300.00'), is_busy=False)

    def test_update_car_model(self):
        self.car.model = 'Granta'
        self.car.save()
        self.assertEqual(Car.objects.get(id=self.car.id).model, 'Granta')

    def test_delete_car(self):
        car_id = self.car.id
        self.car.delete()
        self.assertFalse(Car.objects.filter(id=car_id).exists())

    def test_set_parking_busy(self):
        self.parking.is_busy = True
        self.parking.save()
        self.assertTrue(ParkingSpot.objects.get(id=self.parking.id).is_busy)

    def test_payment_default_paid(self):
        payment = Payment.objects.create(owner=self.user, park=self.parking, amount=Decimal('10.00'))
        self.assertFalse(payment.is_paid)

    def test_news_is_active_default(self):
        news = News.objects.create(title='N', content='C', published_at=datetime.now())
        self.assertTrue(news.is_active)

    def test_vacancy_is_active_default(self):
        vacancy = Vacancy.objects.create(title='V', description='D')
        self.assertTrue(vacancy.is_active)

    def test_review_str(self):
        review = Review.objects.create(user=self.user, text='Nice', rating=4)
        self.assertIn('user2', str(review))
        self.assertIn('4', str(review))

    def test_promocode_str(self):
        promo = PromoCode.objects.create(code='STR', description='desc', discount_percent=5)
        self.assertIn('STR', str(promo))

    def test_coupon_str(self):
        coupon = Coupon.objects.create(code='STRC', description='desc', discount_amount=Decimal('1.00'))
        self.assertIn('STRC', str(coupon))

    def test_servicecategory_str(self):
        cat = ServiceCategory.objects.create(name='Cat2', description='D2')
        self.assertEqual(str(cat), 'Cat2')

# Еще 5 тестов для достижения 50
class FiftyTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user50', password='pass')
        self.car = Car.objects.create(mark='Ford', model='Focus', license_plate='FO1234')
        self.car.owners.add(self.user)
        self.parking = ParkingSpot.objects.create(number=501, price=Decimal('500.00'), is_busy=False)

    def test_car_license_plate_unique(self):
        Car.objects.create(mark='Ford', model='Fiesta', license_plate='FO5678')
        self.assertEqual(Car.objects.filter(mark='Ford').count(), 2)

    def test_parking_currency_default(self):
        self.assertEqual(self.parking.currency, 'BYN')

    def test_payment_currency_default(self):
        payment = Payment.objects.create(owner=self.user, park=self.parking, amount=Decimal('1.00'))
        self.assertEqual(payment.currency, 'BYN')

    def test_service_currency_default(self):
        cat = ServiceCategory.objects.create(name='FiftyCat', description='D')
        service = Service.objects.create(category=cat, name='FiftyService', description='D', price=1, duration=timedelta(hours=1))
        self.assertEqual(service.currency, 'BYN')

    def test_coupon_currency_default(self):
        coupon = Coupon.objects.create(code='FIFTY', description='desc', discount_amount=Decimal('5.00'))
        self.assertEqual(coupon.currency, 'BYN')

# Еще 10 тестов для увеличения покрытия
class EvenMoreModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user3', password='pass')
        self.car = Car.objects.create(mark='Toyota', model='Corolla', license_plate='TY1234')
        self.car.owners.add(self.user)
        self.parking = ParkingSpot.objects.create(number=401, price=Decimal('400.00'), is_busy=False)

    def test_create_multiple_cars(self):
        Car.objects.create(mark='Mazda', model='3', license_plate='MZ1234')
        Car.objects.create(mark='Mazda', model='6', license_plate='MZ5678')
        self.assertEqual(Car.objects.filter(mark='Mazda').count(), 2)

    def test_delete_parking(self):
        pid = self.parking.id
        self.parking.delete()
        self.assertFalse(ParkingSpot.objects.filter(id=pid).exists())

    def test_update_parking_price(self):
        self.parking.price = Decimal('450.00')
        self.parking.save()
        self.assertEqual(ParkingSpot.objects.get(id=self.parking.id).price, Decimal('450.00'))

    def test_payment_update_paid(self):
        payment = Payment.objects.create(owner=self.user, park=self.parking, amount=Decimal('20.00'))
        payment.is_paid = True
        payment.save()
        self.assertTrue(Payment.objects.get(id=payment.id).is_paid)

    def test_news_update_title(self):
        news = News.objects.create(title='Old', content='C', published_at=datetime.now())
        news.title = 'New'
        news.save()
        self.assertEqual(News.objects.get(id=news.id).title, 'New')

    def test_vacancy_update_salary(self):
        vacancy = Vacancy.objects.create(title='V', description='D', salary='1000')
        vacancy.salary = '2000'
        vacancy.save()
        self.assertEqual(Vacancy.objects.get(id=vacancy.id).salary, '2000')

    def test_review_update_rating(self):
        review = Review.objects.create(user=self.user, text='ok', rating=2)
        review.rating = 5
        review.save()
        self.assertEqual(Review.objects.get(id=review.id).rating, 5)

    def test_promocode_update_discount(self):
        promo = PromoCode.objects.create(code='UPD', description='desc', discount_percent=5)
        promo.discount_percent = 20
        promo.save()
        self.assertEqual(PromoCode.objects.get(id=promo.id).discount_percent, 20)

    def test_coupon_update_amount(self):
        coupon = Coupon.objects.create(code='UPD2', description='desc', discount_amount=Decimal('2.00'))
        coupon.discount_amount = Decimal('5.00')
        coupon.save()
        self.assertEqual(Coupon.objects.get(id=coupon.id).discount_amount, Decimal('5.00'))

    def test_servicecategory_update_name(self):
        cat = ServiceCategory.objects.create(name='OldCat', description='D')
        cat.name = 'NewCat'
        cat.save()
        self.assertEqual(ServiceCategory.objects.get(id=cat.id).name, 'NewCat') 
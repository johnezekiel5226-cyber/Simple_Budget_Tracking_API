from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from .models import Transaction
from rest_framework.authtoken.models import Token


User = get_user_model()

class TransactionAPITests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='u1', password='pass1234')
        self.user2 = User.objects.create_user(username='u2', password='pass1234')

def setUp(self):
    self.user1 = User.objects.create_user(username='u1', password='pass1234')
    self.user2 = User.objects.create_user(username='u2', password='pass1234')

    # Create token for user1 to authenticate API requests
    from rest_framework.authtoken.models import Token
    self.token1 = Token.objects.create(user=self.user1)

    # Authenticate test client using DRF TokenAuthentication
    self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)

    def test_create_transaction_requires_positive_amount(self):
        self.client.login(username='u1', password='pass1234')
        url = reverse('transactions-list')
        response = self.client.post(url, {
            "transaction_type": "EXPENSE",
            "category": "FOOD",
            "amount": "5.00",
            "date": "2025-12-10"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_cannot_view_other_users_transaction(self):
        Transaction.objects.create(owner=self.user2, transaction_type='INCOME', category='SALARY', amount=100, date='2025-01-01')
        self.client.login(username='u1', password='pass1234')
        url = reverse('transactions-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # user1 should see zero transactions
        self.assertEqual(len(response.json().get('results', response.json())), 0)


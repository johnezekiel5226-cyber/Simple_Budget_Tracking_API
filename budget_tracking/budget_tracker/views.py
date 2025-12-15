# budget_tracker/views.py
from rest_framework import viewsets, permissions, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Transaction
from .serializers import TransactionSerializer, UserSerializer
from .permissions import IsOwnerOrReadOnly
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
import csv
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


User = get_user_model()

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        # users can only see their own transactions
        return Transaction.objects.filter(owner=self.request.user).order_by('-date', '-created_at')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class ExportCSVView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = Transaction.objects.filter(user=request.user)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="transactions.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Transaction Type',
            'Category',
            'Amount',
            'Date',
            'Description'
        ])

        for t in transactions:
            writer.writerow([
                t.get_transaction_type_display(),
                t.category,
                t.amount,
                t.date,
                t.description
            ])

        return response

class ExportPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="transactions.pdf"'

        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4

        y = height - 40
        p.setFont("Helvetica", 10)

        p.drawString(40, y, "Budget Transactions Report")
        y -= 30

        transactions = Transaction.objects.filter(user=request.user)

        for t in transactions:
            line = f"{t.date} | {t.get_transaction_type_display()} | {t.category} | {t.amount}"
            p.drawString(40, y, line)
            y -= 20

            if y < 40:
                p.showPage()
                p.setFont("Helvetica", 10)
                y = height - 40

        p.showPage()
        p.save()

        return response


class UserViewSet(viewsets.ModelViewSet):
    """
    Basic user CRUD. Password write-only; we create users using create_user().
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]  # Restrict as desired (e.g., admin-only for list)

    def get_permissions(self):
        # Allow registration (create) to unauthenticated users, but restrict retrieve/update/delete
        if self.action in ['create']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        # Optionally restrict user list to admin only
        if not request.user.is_staff:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        return super().list(request, *args, **kwargs)

class ObtainAuthTokenAndUser(APIView):
    """
    Optional: return token + user on login
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        from django.contrib.auth import authenticate
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key, "user": UserSerializer(user).data})
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

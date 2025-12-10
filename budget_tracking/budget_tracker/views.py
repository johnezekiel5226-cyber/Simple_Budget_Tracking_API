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
from rest_framework import status

User = get_user_model()

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        # users can only see their own transactions
        return Transaction.objects.filter(owner=self.request.user).order_by('-date', '-created_at')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

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

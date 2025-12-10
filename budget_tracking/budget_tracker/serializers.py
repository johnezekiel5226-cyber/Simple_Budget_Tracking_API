# budget_tracker/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Transaction

User = get_user_model()

class TransactionSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Transaction
        fields = ['id', 'owner', 'transaction_type', 'category', 'amount', 'date', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be a positive number.")
        return value

    def validate(self, data):
        # Ensure required fields are present: transaction_type, amount, date
        if 'transaction_type' not in data and self.instance is None:
            raise serializers.ValidationError({"transaction_type": "This field is required."})
        if 'amount' not in data and self.instance is None:
            raise serializers.ValidationError({"amount": "This field is required."})
        if 'date' not in data and self.instance is None:
            raise serializers.ValidationError({"date": "This field is required."})
        return data

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        read_only_fields = ['id']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user

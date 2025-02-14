import phonenumbers
from phonenumbers import is_valid_number

from rest_framework.serializers import ModelSerializer, Serializer, ListField, ValidationError, IntegerField
from .models import Order, OrderItem


class OrderItemSerializer(Serializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity',]



class OrderSerializer(ModelSerializer):
    products = ListField(child=OrderItemSerializer())

    class Meta:
        model = Order
        fields = ['firstname', 'lastname', 'phonenumber', 'address', 'products']

        def phone_number_validator(self):
            parsed_number = phonenumbers.parse('phonenumber', None)
            if not is_valid_number(parsed_number):
                raise ValidationError("phonenumber: Введен некорректный номер телефона.")

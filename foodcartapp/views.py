import json
import phonenumbers
from phonenumbers import is_valid_number
from rest_framework.serializers import ValidationError
from .serializers import OrderItemSerializer, OrderSerializer

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product, Order, OrderItem


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['GET'])
def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return Response(dumped_products)


@api_view(['POST'])
def register_order(request):
    try:
        order_serializer = OrderSerializer(data=request.data)
        order_serializer.is_valid(raise_exception=True)

        order_items = order_serializer.validated_data['products']

        order = Order.objects.create(
            firstname=order_serializer.validated_data['firstname'],
            lastname=order_serializer.validated_data['lastname'],
            phonenumber=order_serializer.validated_data['phonenumber'],
            address=order_serializer.validated_data['address'],
        )
        order_itemsss = [
            OrderItem(
                order=order,
                product=order_items[0],
                quantity=order_items[1],
                price=order_items,
            )

        ]

        OrderItem.objects.bulk_create(order_itemsss)

        return Response({"message": "Заказ принят!", "data": order_serializer.data}, status=201)

    except ValidationError as e:
        return Response({'error': str(e)}, status=422)

    except Product.DoesNotExist:
        return Response({'error': 'Заказ с неуществующим id продукта'}, status=404)

    except json.JSONDecodeError:
        return Response({'error': 'Некорректный JSON'}, status=400)

    except Exception as e:
        return Response({'error': str(e)}, status=500)

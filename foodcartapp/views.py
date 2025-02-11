import json

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
        data = request.data

        order = Order.objects.create(
            firstname=data.get('firstname'),
            lastname=data.get('lastname'),
            phonenumber=data.get('phonenumber'),
            address=data.get('address'),
        )

        products = data.get('products', [])
        order_items = []

        for item in products:
            product_id = item.get('product')
            quantity = item.get('quantity', 1)

            product = Product.objects.get(id=product_id)

            order_items.append(OrderItem(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            ))

        OrderItem.objects.bulk_create(order_items)

        return Response({"message": "Заказ обработан!", "data": data})

    except Product.DoesNotExist:
        return Response({'error': 'Товар не найден'}, status=404)

    except json.JSONDecodeError:
        return Response({'error': 'Некорректный JSON'}, status=400)

    except Exception as e:
        return Response({'error': str(e)}, status=500)

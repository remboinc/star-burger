import json
import phonenumbers
from phonenumbers import is_valid_number


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


class EmptyProductListError(Exception):
    def __init__(self, message):
        super().__init__(message)


@api_view(['POST'])
def register_order(request):
    try:
        data = request.data

        if not all(field in data for field in ['firstname', 'lastname', 'phonenumber', 'address']):
            raise ValueError('firstname, lastname, phonenumber, address: Обязательное поле')

        if 'products' not in data:
            raise EmptyProductListError('products: Обязательное поле')

        if data['firstname'] is None and data['lastname'] is None and data['phonenumber'] is None and data['address'] is None:
            raise EmptyProductListError('firstname, lastname, phonenumber, address: Это поле не может быть пустым.')

        elif data['firstname'] is None:
            raise EmptyProductListError('firstname: Это поле не может быть пустым.')

        if not data['phonenumber']:
            raise EmptyProductListError('phonenumber: Это поле не может быть пустым.')

        parsed_number = phonenumbers.parse(data['phonenumber'], None)
        if not is_valid_number(parsed_number):
            raise ValueError("phonenumber: Введен некорректный номер телефона.")

        if not isinstance(data['firstname'], str):
            raise ValueError("firstname: Not a valid string.")

        order = Order.objects.create(
            firstname=data.get('firstname'),
            lastname=data.get('lastname'),
            phonenumber=data.get('phonenumber'),
            address=data.get('address'),
        )

        if isinstance(data['products'], str):
            raise EmptyProductListError('products: Ожидается список, а не строка.')

        if len(data['products']) == 0:
            raise EmptyProductListError('products: Этот список не может быть пустым.')

        if data['products'] is None:
            raise EmptyProductListError('products: Это поле не может быть пустым.')

        order_items = []

        for item in data['products']:
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

        return Response({"message": "Заказ принят!", "data": data})

    except ValueError as e:
        return Response({'error': str(e)}, status=422)

    except Product.DoesNotExist:
        return Response({'error': 'Заказ с неуществующим id продукта'}, status=404)

    except json.JSONDecodeError:
        return Response({'error': 'Некорректный JSON'}, status=400)

    except EmptyProductListError as e:
        return Response({'error': str(e)}, status=422)

    except Exception as e:
        return Response({'error': str(e)}, status=500)

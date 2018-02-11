import json

from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from oauth2_provider.models import AccessToken

from waimaiapp.models import Restaurant, Meal, Order, OrderDetails
from waimaiapp.serializers import RestaurantSerializer, MealSerializer

def customer_get_restaurants(request):
    restaurants = RestaurantSerializer(
    Restaurant.objects.all().order_by("-id"),
    many = True,
    context = {"request": request}
    ).data

    return JsonResponse({"restaurants": restaurants})

def customer_get_meals(request, restaurant_id):
    meals = MealSerializer(
        Meal.objects.filter(restaurant_id = restaurant_id).order_by("-id"),
        many = True,
        context = {"request": request}
    ).data

    return JsonResponse({"meals": meals})

@csrf_exempt
def customer_add_order(request):


    if request.method == "POST":
        # Get token
        access_token = AccessToken.objects.get(token = request.POST.get("access_token"), expires__gt = timezone.now())
        # Get profile
        customer = access_token.user.customer

        # Check whether has order that is not delivered yet
        if Order.objects.filter(customer = customer).exclude(status = Order.DELIVERED):
            return JsonResponse({"status": "fail", "error": "Your last order must be completed"})

        # Check the address
        if not request.POST["address"]:
            return JsonResponse({"status": "fail", "error": "Address is required"})

        # Get order details
        order_details = json.loads(request.POST["order_details"])

        order_total = 0
        for meal in order_details:
            order_total += Meal.objects.get(id = meal["meal_id"]).price * meal["quantity"]

        if len(order_details) > 0:
            # Step 1 - Create an order
            order = Order.objects.create(
            customer = customer,
            restaurant_id = request.POST["restaurant_id"],
            total = order_total,
            status = Order.COOKING,
            address = request.POST["address"]
            )

            # Step 2 - Create order details
            for meal in order_details:
                OrderDetails.objects.create(
                    order = order,
                    meal_id = meal["meal_id"],
                    quantity = meal["quantity"],
                    sub_total = Meal.objects.get(id = meal["meal_id"]).price * meal["quantity"]
                )
            return JsonResponse({"status": "success"})

def customer_get_latest_order(request):
    return JsonResponse({})

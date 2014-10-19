from django.shortcuts import render, redirect, get_object_or_404,\
    get_list_or_404
from django.http import Http404
from django.http import HttpResponse
from reservetion.models import *
from reservetion.forms import *
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from datetime import datetime
from django.db.models import Q
import json
from django.views.decorators.csrf import csrf_protect


@require_http_methods(["GET", "POST"])
@never_cache
def sign(request):
    if request.method == 'POST':
        form = SignForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('loginUser'))
        return render(request, 'reservetion/sign.html', {'form': form})
    else:
        form = SignForm()
        return render(request, 'reservetion/sign.html', {'form': form})


@require_http_methods(["GET", "POST"])
@never_cache
def logoutUser(request):
    logout(request)
    return redirect(reverse('loginUser'))


@require_http_methods(["GET", "POST"])
@never_cache
def loginUser(request, **Kargs):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if not clientHasOrder(user.id):
                        if hasCart(user.id):
                            cart = getCart(user.id)
                            for item in cart.getCartPizzas():
                                item.delete()
                            for item in cart.getCartDrinks():
                                item.delete()
                            cart.delete()
                        cart = Cart(
                            client=user, alt=user.client.alt,
                            lng=user.client.lng)
                        cart.save()
                    return HttpResponseRedirect(reverse('menu'))
            msg = "Invalid e-mail or password "
            return render(request, 'reservetion/login.html', {'form': form,
                                                              'msg': msg})
    else:
        form = LoginForm()
    return render(request, 'reservetion/login.html', {'form': form})


@require_http_methods(["GET", "POST"])
@never_cache
@login_required()
def cart(request):
    client_id = request.user.id
    cart = Cart.objects.get(client_id=client_id)
    context = {'cart': cart}
    return render(request, 'reservetion/cart.html', context)


@require_http_methods(["GET", "POST"])
@never_cache
@login_required()
def order(request):
    client_id = request.user.id
    order = Order.objects.get(client__id=client_id)
    context = {'order': order}
    return render(request, 'reservetion/order.html', context)


# optimise
@require_http_methods(["GET", "POST"])
@never_cache
@login_required()
def selected(request, item_id, itemtype):
    client_id = request.user.id
    if int(itemtype) == 1:
        pizza = get_object_or_404(Pizza, pk=item_id)
        if request.method == 'POST':
            form = OptionForm(request.POST, pizza_id=item_id)
            if form.is_valid():
                form.save_pizza(pizza=pizza, client_id=client_id)
                messages.success(
                    request, ' %s add to you cart.' % pizza.pizza_name,
                    fail_silently=True)
                return redirect(reverse('menu'))
        else:
            form = OptionForm(pizza_id=item_id)
            return render(request, 'reservetion/pizza_slected.html',
                          {'form': form, 'pizza': pizza, 'pizza_id': item_id})
    elif int(itemtype) == 2:
        drink = get_object_or_404(Drink, pk=item_id)
        if request.method == 'POST':
            form = DrinkForm(request.POST)
            if form.is_valid():
                form.save_drink(drink=drink, client_id=client_id)
                messages.success(
                    request, ' %s add to you cart.' % drink.drink_name,
                    fail_silently=True)
                return redirect(reverse('menu'))
        else:
            form = DrinkForm()
            return render(request, 'reservetion/drink_slected.html',
                          {'form': form, 'drink': drink, 'drink_id': item_id})


@csrf_protect
@require_http_methods("POST")
@never_cache
@login_required()
def incrementQuantity(request, item_id, itemtype):
    data = {}
    if int(itemtype) == 1:
        r = ItemPizza.objects.get(pk=item_id)
        r.incQuantity()
    elif int(itemtype) == 2:
        r = ItemDrink.objects.get(pk=item_id)
        r.incQuantity()
    data['new'] = r.quantity
    data['stat'] = "ok"
    return HttpResponse(json.dumps(data), mimetype="application/json")


@csrf_protect
@require_http_methods("POST")
@never_cache
@login_required()
def decreaseQuantity(request, item_id, itemtype):
    data = {}
    if int(itemtype) == 1:
        r = ItemPizza.objects.get(pk=item_id)
    elif int(itemtype) == 2:
        r = ItemDrink.objects.get(pk=item_id)
    if r.quantity > 1:
        r.decQuantity()
    data['new'] = r.quantity
    data['stat'] = "ok"
    return HttpResponse(json.dumps(data), mimetype="application/json")


@require_http_methods(["GET", "POST"])
@never_cache
@login_required()
def deletetItem(request, item_id, itemtype):
    if int(itemtype) == 1:
        r = ItemPizza.objects.get(pk=item_id)
    elif int(itemtype) == 2:
        r = ItemDrink.objects.get(pk=item_id)
    messages.success(request, 'Item %s delete with success.' % r.id)
    r.delete()
    return redirect(reverse('cart'))


@require_http_methods(["GET", "POST"])
@never_cache
@login_required()
def payment(request):
    client_id = request.user.id
    if request.method == 'POST':
        form = PaymenForm(request.POST)
        if form.is_valid():
            client = User.objects.get(id=client_id)
            cart = get_object_or_404(Cart, client__id=client_id)
            order = Order(client=client, time=datetime.now(),
                          timetodelvry=cart.timetodelvry, alt=cart.alt,
                          lng=cart.lng, typeDelivry=cart.typeDelivry,
                          typeDelivryoption=cart.typeDelivryoption)
            order.save()
            for i in cart.itemspizza.all():
                order.itemspizza.add(i)
            for i in cart.itemsdrink.all():
                order.itemsdrink.add(i)
            cart.delete()
            messages.success(
                request, "You have new order ,you can't order another \
                until this order is delivred", fail_silently=True)
            return HttpResponseRedirect(reverse('menu'))
    else:
        form = AdresseForm()
    return render(request, 'reservetion/payment.html', {'form': form})


# optimise


@require_http_methods(["GET", "POST"])
@never_cache
@login_required()
def adreesse(request):
    client_id = request.user.id
    if request.method == 'POST':
        form = AdresseForm(request.POST)
        if form.is_valid():
            alt = form.cleaned_data['alt']
            lng = form.cleaned_data['lng']
            cart = get_object_or_404(Cart, client__id=client_id)
            cart.alt = alt
            cart.lng = lng
            cart.save()
            return HttpResponseRedirect(reverse('payment'))
    else:
        client = User.objects.get(id=client_id)
        data = {'adresse': client.client.address,
                'phone': client.client.phone,
                'alt': client.client.alt,
                'lng': client.client.lng,
                }
        form = AdresseForm(data)
    return render(request, 'reservetion/adresse.html', {'form': form})

# optimise


@require_http_methods(["GET", "POST"])
@never_cache
@login_required()
def checkout(request):
    client_id = request.user.id
    if request.method == 'POST':
        form = DeliveryTypeForm(request.POST)
        if form.is_valid():
            delivry_type = form.cleaned_data['delivry_type']
            option = form.cleaned_data['option']
            timeclean = form.cleaned_data['time']
            cart = get_object_or_404(Cart, client__id=client_id)
            cart.typeDelivry = delivry_type
            cart.typeDelivryoption = option
            cart.time = datetime.now()

            if option == 'A':
                cart.timetodelvry = datetime.strptime(
                    timeclean, '%Y-%m-%d %H:%M:%S')
                cart.save()
                if delivry_type == 'D':
                    return redirect(reverse('adreesse'))
            cart.save()
            return redirect(reverse('payment'))
    else:
        form = DeliveryTypeForm()
    return render(request, 'reservetion/checkout.html', {'form': form})

# optimise


@require_http_methods(["GET", "POST"])
@never_cache
@login_required()
def editItem(request, item_id):
    client_id = request.user.id
    item = get_object_or_404(ItemPizza, pk=item_id)
    if request.method == 'POST':
        form = OptionForm(request.POST, pizza_id=item.pizza.id)
        if form.is_valid():
            item.toppings.clear()
            form.update(item=item)
            messages.success(request, ' %s Item Update.' %
                             item.id, fail_silently=True)
            return redirect(reverse('cart'))
        return render(request, 'reservetion/pizza_slected.html',
                      {'form': form, 'pizza': pizza,
                       'pizza_id': reserv.pizza.id, 'client_id': client_id})
    else:
        topping = item.toppings.all()
        data = {'quantity': item.quantity,
                'sauce': topping.get(topping_option='K').id,
                'size': Size.objects.get(pizza__id=item.pizza.id,
                                         size=item.size).id,
                'drink': [l.id for l in topping.filter(topping_option='D')],
                'supplement_meat':
                [l.id for l in topping.filter(topping_option='S')],
                'supplement_no_meat':
                [l.id for l in topping.filter(topping_option='L')],
                'cheese':
                [l.id for l in topping.filter(topping_option='C')],
                }
        form = OptionForm(data, pizza_id=item.pizza.id)
        return render(request, 'reservetion/edit.html',
                      {'form': form, 'pizza': item.pizza,
                       'pizza_id': item.pizza.id, 'item_id': item.id})


@require_http_methods(["GET", "POST"])
@never_cache
@login_required()
@permission_required('reservetion.add_cart', raise_exception=True)
def menu(request):
    client_id = request.user.id

    pizzasclassic = Pizza.objects.filter(pizza_menu='C')
    paginator = Paginator(pizzasclassic, 4)
    page = request.GET.get('page')
    try:
        pizzaclassic = paginator.page(page)
    except PageNotAnInteger:
        pizzaclassic = paginator.page(1)
    except EmptyPage:
        pizzaclassic = paginator.page(paginator.num_pages)

    pizzasspecial = Pizza.objects.filter(pizza_menu='S')
    paginator = Paginator(pizzasspecial, 4)
    page2 = request.GET.get('page2')
    try:
        pizzaspecial = paginator.page(page2)
    except PageNotAnInteger:
        pizzaspecial = paginator.page(1)
    except EmptyPage:
        pizzaspecial = paginator.page(paginator.num_pages)

    drink_all = Drink.objects.all()
    paginator2 = Paginator(drink_all, 4)
    page2 = request.GET.get('pagedrink')
    try:
        drink = paginator2.page(page2)
    except PageNotAnInteger:
        drink = paginator2.page(1)
    except EmptyPage:
        drink = paginator2.page(paginator2.num_pages)

    if clientHasOrder(client_id):
        order = getOrdre(client_id)
        context = {'order': order,
                   'pizzaspecial': pizzaspecial, 'pizzasclassic': pizzaclassic,
                   'drinkslist': drink_all
                   }
    else:
        cart = Cart.objects.get(client__id=client_id)
        context = {'cart': cart,
                   'pizzaspecial': pizzaspecial, 'pizzasclassic':
                   pizzaclassic, 'drinkslist': drink_all}
    return render(request, 'reservetion/partial_menu/menu.html', context)

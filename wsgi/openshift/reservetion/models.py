from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum


class Client(models.Model):
    user = models.OneToOneField(User)
    address = models.CharField(max_length=30)
    phone = models.IntegerField()
    alt = models.DecimalField(
        "google map altitude", max_digits=18, decimal_places=16)
    lng = models.DecimalField(
        "google map long", max_digits=18, decimal_places=16)

    class Meta:
        db_table = 'UserClient'


class Size(models.Model):
    choice = (('Small', 'Small'), ('Meduim', 'Meduim'), ('Large', 'Large'))
    size = models.CharField("size", max_length=10, choices=choice)
    num_slides = models.IntegerField("number of slides", max_length=1)
    size_price = models.DecimalField(
        "pizza price ", max_digits=6, decimal_places=3)

    class Meta:
        db_table = 'Size'

    def __unicode__(self):
        return self.size + " " + str(self.size_price) + " " +\
            str(self.num_slides)


class Pizza(models.Model):
    choice = (('C', 'Classic'), ('S', 'Special'))
    pizza_name = models.CharField("pizza  label", max_length=30)
    image = models.ImageField(upload_to='image')
    sizes = models.ManyToManyField(Size)
    pizza_description = models.CharField("pizza  desccription", max_length=150)
    pizza_menu = models.CharField("menu", max_length=30, choices=choice)

    def __unicode__(self):
        return "Pizza" + self.pizza_name

    class Meta:
        db_table = 'Pizza'
        ordering = ['pizza_name']


class Drink(models.Model):

    drink_name = models.CharField("drink  label", max_length=30)
    image = models.ImageField(upload_to='image')
    size_drink = models.DecimalField(
        "drink price ", max_digits=6, decimal_places=3)

    def __unicode__(self):
        return "Drink" + self.drink_name

    class Meta:
        db_table = 'Drink'
        ordering = ['drink_name']


class Topping(models.Model):
    choice = (('S', 'Supplement Meat'), ('L', 'Supplement no Meat'),
              ('C', 'Cheese'), ('K', 'Sauce'))
    topping_option = models.CharField("option", max_length=30, choices=choice)
    topping_name = models.CharField("Supplement's name", max_length=30)
    topping_price = models.DecimalField(
        "Supplement's price", max_digits=6, decimal_places=3)
    topping_description = models.CharField(
        "Supplement's desccription", max_length=150, blank=True)

    class Meta:
        db_table = 'Topping'

    def __unicode__(self):
        return self.topping_name + ' ' + str(self.topping_price)


class Item(models.Model):

    total_price = models.DecimalField(
        "SubTotal price's pizza", max_digits=6, decimal_places=3)
    unit_price = models.DecimalField(
        "Unit price's pizza", max_digits=6, decimal_places=3)

    class Meta:
        abstract = True


class ItemPizza(Item):
    pizza = models.ForeignKey(
        'reservetion.Pizza', verbose_name='ordered pizza')
    toppings = models.ManyToManyField(Topping, blank=True)
    size = models.CharField("size of pizza", max_length=10)
    quantity = models.IntegerField('quantity ')

    def getOption(self):
        return [l.topping_name for l in self.toppings.all()]

    def incQuantity(self):
        self.quantity += 1
        self.total_price = self.quantity * self.unit_price
        self.save()

    def decQuantity(self):
        self.quantity -= 1
        self.total_price = self.quantity * self.unit_price
        self.save()

    class Meta:
        db_table = 'ItemPizza'


class ItemDrink(Item):
    drink = models.ForeignKey(
        'reservetion.Drink', verbose_name='ordered drink')
    quantity = models.IntegerField('quantity ')

    def incQuantity(self):
        self.quantity += 1
        self.total_price = self.quantity * self.unit_price
        self.save()

    def decQuantity(self):
        self.quantity -= 1
        self.total_price = self.quantity * self.unit_price
        self.save()

    class Meta:
        db_table = 'ItemDrink'


class Cart(models.Model):
    client = models.OneToOneField(User)
    itemspizza = models.ManyToManyField(ItemPizza)
    itemsdrink = models.ManyToManyField(ItemDrink)
    time = models.DateTimeField('time of reservation', blank=True, null=True)
    timetodelvry = models.DateTimeField(
        'time of reservation', blank=True, null=True)
    alt = models.DecimalField(
        "google map altitude", max_digits=16, decimal_places=14, blank=True,
        null=True)
    lng = models.DecimalField(
        "google map long", max_digits=16, decimal_places=14, blank=True,
        null=True)
    typeDelivry = models.CharField(
        "type delivry", max_length=10, blank=True, null=True)
    typeDelivryoption = models.CharField(
        "option type delivry", max_length=10, blank=True, null=True)

    class Meta:
        db_table = 'Cart'

    def getCartTotal(self):
        pizzas = self.itemspizza.all()
        total1 = pizzas.aggregate(totalpizza=Sum('total_price'))
        drinks = self.itemsdrink.all()
        total2 = drinks.aggregate(totaldrink=Sum('total_price'))
        if total1['totalpizza'] and total2['totaldrink']:
            total = total1['totalpizza'] + total2['totaldrink']
        elif total1['totalpizza'] is None:
            total = total2['totaldrink']
        elif total2['totaldrink'] is None:
            total = total1['totalpizza']
        return total

    def getCartPizzas(self):
        return self.itemspizza.all()

    def getCartDrinks(self):
        return self.itemsdrink.all()


class Order(models.Model):
    client = models.ForeignKey(User, verbose_name='client')
    itemspizza = models.ManyToManyField(ItemPizza)
    itemsdrink = models.ManyToManyField(ItemDrink)
    time = models.DateTimeField('time of reservation', blank=True, null=True)
    timetodelvry = models.DateTimeField(
        'time of reservation', blank=True, null=True)
    alt = models.DecimalField(
        "google map altitude", max_digits=16, decimal_places=14, blank=True,
        null=True)
    lng = models.DecimalField(
        "google map long", max_digits=16, decimal_places=14, blank=True,
        null=True)
    typeDelivry = models.CharField("type delivry", max_length=10)
    typeDelivryoption = models.CharField(
        "option type delivry", max_length=10, blank=True, null=True)

    class Meta:
        db_table = 'Order'

    def getOrderTotal(self):
        pizzasorder = self.itemspizza.all()
        total1 = pizzasorder.aggregate(totalpizza=Sum('total_price'))
        drinksorder = self.itemsdrink.all()
        total2 = drinksorder.aggregate(totaldrink=Sum('total_price'))
        if total1['totalpizza'] and total2['totaldrink']:
            totalorder = total1['totalpizza'] + total2['totaldrink']
        elif total1['totalpizza'] is None:
            totalorder = total2['totaldrink']
        elif total2['totaldrink'] is None:
            totalorder = total1['totalpizza']
        return totalorder

    def getOrderPizzas(self):
        return self.itemspizza.all()

    def getOrderDrinks(self):
        return self.itemsdrink.all()


class Delivery_Man(models.Model):
    first_name = models.CharField("person's first name", max_length=30)
    last_name = models.CharField("person's last name", max_length=30)
    cin = models.IntegerField('carte identite national', max_length=8)

    def __unicode__(self):
        return "Delivery Man :" + str(self.cin)

    class Meta:
        db_table = 'Delivery_Man'
        ordering = ['cin']


def getCart(client_id):
    return Cart.objects.get(client__id=client_id)


def hasCart(client_id):
    return Cart.objects.filter(client__id=client_id).exists()


def getOrdre(client_id):
    return Order.objects.get(client__id=client_id)


def clientHasOrder(client_id):
    return Order.objects.filter(client__id=client_id).exists()

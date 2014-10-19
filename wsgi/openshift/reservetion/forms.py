from django import forms
from django.forms import ModelForm, TextInput, PasswordInput,\
    ModelChoiceField, ModelMultipleChoiceField
from reservetion.models import *
from django.contrib.auth.models import User, Group
from datetime import time, datetime, timedelta
from django.shortcuts import get_object_or_404


class MyModelChoiceField1(ModelChoiceField):

    def label_from_instance(self, obj):
        return obj.size


class MyModelChoiceField2(ModelChoiceField):

    def label_from_instance(self, obj):
        return obj.topping_name


class MyModelMultipleChoiceField(ModelMultipleChoiceField):

    def label_from_instance(self, obj):
        return obj.topping_name


class LoginForm(forms.Form):
    username = forms.CharField(max_length=30, widget=forms.TextInput(
        attrs={'placeholder': 'Username', 'class': "form-control",
               'required': 'True'}))
    password = forms.CharField(max_length=30, widget=forms.PasswordInput(
        attrs={'placeholder': 'Password', 'class': "form-control",
               'required': 'True'}))


class DrinkForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=50, initial=1)

    def save_drink(self, *args, **kwargs):
        drink = kwargs.pop('drink')
        client_id = kwargs.pop('client_id')
        cart = get_object_or_404(Cart, client__id=client_id)
        quantity = self.cleaned_data['quantity']
        item = ItemDrink(
            drink=drink, quantity=quantity,
            total_price=quantity * drink.size_drink,
            unit_price=drink.size_drink)
        item.save()
        cart.itemsdrink.add(item)
        return item


class OptionForm(forms.Form):
    size = MyModelChoiceField1(widget=forms.Select(
        attrs={'required': 'True'}), queryset=Size.objects.all(),
        empty_label='Select a Size')
    cheese = MyModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple, required=False,
        queryset=Topping.objects.all())
    sauce = MyModelChoiceField2(widget=forms.RadioSelect(
        attrs={'required': 'True'}),
        queryset=Topping.objects.all().filter(topping_option="K"),
        empty_label=None)
    supplement_meat = MyModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple, required=False,
        queryset=Topping.objects.all())
    supplement_no_meat = MyModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple, required=False,
        queryset=Topping.objects.all())
    quantity = forms.IntegerField(min_value=1, max_value=50, initial=1)

    def __init__(self, *args, **kwargs):
        pizza_id = kwargs.pop('pizza_id')
        super(OptionForm, self).__init__(*args, **kwargs)
        self.fields['cheese'].queryset = Topping.objects.all().filter(
            topping_option="C")
        self.fields['sauce'].queryset = Topping.objects.all().filter(
            topping_option="K")
        self.fields['supplement_meat'].queryset = Topping.objects.all().filter(
            topping_option="S")
        self.fields['supplement_no_meat'].queryset = Topping.objects.all().filter(
            topping_option="L")
        self.fields['size'].queryset = Size.objects.filter(pizza__id=pizza_id)

    def save_pizza(self, *args, **kwargs):
        pizza = kwargs.pop('pizza')
        client_id = kwargs.pop('client_id')
        cart = get_object_or_404(Cart, client__id=client_id)
        sauce = self.cleaned_data['sauce']
        quantity = self.cleaned_data['quantity']
        size = self.cleaned_data['size']
        item = ItemPizza(pizza=pizza, quantity=quantity,
                         total_price=size.size_price *
                         quantity, size=size.size, unit_price=size.size_price)
        item.save()
        cart.itemspizza.add(item)
        item.toppings.add(sauce)
        add_price = 0
        List = [self.cleaned_data['cheese'], self.cleaned_data[
            'supplement_meat'], self.cleaned_data['supplement_no_meat']]
        for sups in List:
            for suppliment in sups:
                add_price += suppliment.topping_price
                item.toppings.add(suppliment)
            item.total_price = item.total_price + add_price * quantity
            item.save()
        return item

    def update(self, *args, **kwargs):
        item = kwargs.pop('item')
        sauce = self.cleaned_data['sauce']
        quantity = self.cleaned_data['quantity']
        size = self.cleaned_data['size']
        item.quantity = quantity
        item.unit_price = size.size_price
        item.total_price = size.size_price * quantity
        item.size = size.size
        item.toppings.add(sauce)
        add_price = 0
        List = [self.cleaned_data['cheese'], self.cleaned_data[
                'supplement_meat'], self.cleaned_data['supplement_no_meat']]
        for sups in List:
            for suppliment in sups:
                add_price += suppliment.topping_price
                item.toppings.add(suppliment)
        item.total_price = item.total_price + add_price * quantity
        item.save()

# optimise


class SignForm(forms.Form):
    username = forms.CharField(max_length=30, widget=forms.TextInput(
        attrs={'placeholder': 'Username', 'class': "form-control",
               'required': 'True'}))
    first_name = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'First Name', 'class': "form-control",
               'required': 'True'}))
    last_name = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Last Name', 'class': "form-control",
               'required': 'True'}))
    password1 = forms.CharField(max_length=30, widget=forms.PasswordInput(
        attrs={'placeholder': 'Password', 'class': "form-control",
               'required': 'True'}))
    password2 = forms.CharField(max_length=30, widget=forms.PasswordInput(
        attrs={'placeholder': 'Confirme Password', 'class': "form-control",
               'required': 'True'}))
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'placeholder': 'Email', 'class': "form-control",
               'required': 'True'}))
    address = forms.CharField(max_length=30, widget=forms.TextInput(
        attrs={'placeholder': 'Adresse', 'class': "form-control",
               'required': 'True'}))
    phone = forms.IntegerField(
        widget=forms.NumberInput(attrs={'placeholder': 'Phone'}))
    alt = forms.DecimalField("google map altitude", error_messages={
                             'required': 'Please chose your location'},
                             widget=forms.HiddenInput(), max_digits=18,
                             decimal_places=16)
    lng = forms.DecimalField(
        "google map long", widget=forms.HiddenInput(), max_digits=18,
        decimal_places=16)

    def clean_username(self):  # check if username dos not exist before
        try:
            User.objects.get(username=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']

        raise forms.ValidationError("exist already")

    def clean(self):  # check if password 1 and password2 match each other
        # check if both pass first validation
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            # check if they match each other
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError("passwords dont match each other")

        return self.cleaned_data

        # create new user
    def save(self):
        new_user = User.objects.create_user(self.cleaned_data['username'],
                                            self.cleaned_data['email'],
                                            self.cleaned_data['password1'])
        new_user.first_name = self.cleaned_data['first_name']
        new_user.last_name = self.cleaned_data['last_name']
        new_user.save()
        group = Group.objects.get(name='client')
        group.user_set.add(new_user)
        r = Client(user=new_user, address=self.cleaned_data['address'],
                   phone=self.cleaned_data['phone'],
                   alt=self.cleaned_data['alt'], lng=self.cleaned_data['lng'])
        r.save()
        return new_user

# optimise


class DeliveryTypeForm(forms.Form):

    listtime = list()
    datenow = datetime.now()
    datelast = datetime(
        year=datenow.year, month=datenow.month, day=datenow.day,
        hour=23, minute=59)
    while datenow < datelast:
        listtime.append(
            (datenow.strftime("%Y-%m-%d %H:%M:%S"),
             datenow.strftime(" %H:%M:")))
        datenow = datenow + timedelta(minutes=30)
    delivry_type = forms.ChoiceField(widget=forms.RadioSelect(
        attrs={'onclick': 'visibel();', 'required': 'True'}),
        choices=(('P', 'Pick Up Inside'), ('D', 'Delivery')))
    option = forms.ChoiceField(widget=forms.RadioSelect(
                               attrs={'onclick': 'timevisible();',
                                      'required': 'True'}), choices=(
        ('S', 'Soonest Available'), ('A', 'Specific Time')))
    time = forms.ChoiceField(
        widget=forms.Select(), choices=listtime, required=False)

# optimise


class AdresseForm(forms.Form):
    adresse = forms.CharField(widget=forms.TextInput(
        attrs={'required': 'True', 'class': "form-control"}),
        max_length=30, min_length=7)
    phone = forms.IntegerField(
        widget=forms.NumberInput(attrs={'required': 'True',
                                        'class': "form-control"}))
    alt = forms.DecimalField(
        "google map altitude", widget=forms.HiddenInput(),
        max_digits=18, decimal_places=16)
    lng = forms.DecimalField(
        "google map long", widget=forms.HiddenInput(),
        max_digits=18, decimal_places=16)


class PaymenForm(forms.Form):
    pass

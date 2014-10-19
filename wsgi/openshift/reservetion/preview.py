from django.contrib.formtools.preview import FormPreview
from django.http import HttpResponseRedirect
from django.shortcuts import render
from reservetion.models import *


class LoginFormPreview(FormPreview):
	def done(self, request, cleaned_data):
		email=form.cleaned_data['email']
		password=form.cleaned_data['password']
		try:
			client = Client.objects.get(email=email)
		except ObjectDoesNotExist:
			return render(request, 'reservetion/login.html',{'form': form,'msg':"Client doesn't exist"})

		if client.password == password:
			request.session.clear()
			request.session['client_id'] = client.id


			cart=Cart.objects.filter(client__id=client.id)
			cart.delete()
			cart=Cart(client=client)
			cart.save()
			request.session['cart_id'] = cart.id			
			return HttpResponseRedirect(reverse('menu'))

		else:
			msg="Invalid e-mail or password "
			return render(request, 'reservetion/login.html',{'form': form,'msg':msg})

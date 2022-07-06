from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import *
from .restapis import *
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime

import logging
import json

from django import forms

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def get_about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)

# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/login.html', context)
    else:
        return render(request, 'djangoapp/login.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):

    logout(request)

    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://6c8c4165.us-east.apigw.appdomain.cloud/dealership/api/dealership"

        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context['dealerships'] = dealerships

        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealerId):
    if request.method == "GET":

        context = {}
        dealerId = {'dealerId': dealerId}

        # Get dealership details
        url = "https://6c8c4165.us-east.apigw.appdomain.cloud/dealership/api/dealership/dealerId/info"
        dealership = get_dealer_by_id_from_cf(url, dealerId)
        context['dealership'] = dealership

        # Get reviews
        url = "https://6c8c4165.us-east.apigw.appdomain.cloud/dealership/api/dealership/dealerId"
        reviews = get_dealer_reviews_from_cf(url, dealerId)
        context['reviews'] = reviews

        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...

class ReviewForm(forms.Form):
    review = forms.CharField(label='content', max_length=100)
    car = forms.CharField(label='char', max_length=100)

def add_review(request, dealerId):
    
    if request.method == 'GET':

        # Get car models from sqlite
        context = {}
        context["carmodel"] = CarModel.objects.filter(dealership = dealerId)

        # Get dealership information from CF
        url = "https://6c8c4165.us-east.apigw.appdomain.cloud/dealership/api/dealership/dealerId/info"
        dealerId = {'dealerId': dealerId}
        context["dealership"] = get_dealer_by_id_from_cf(url, dealerId)
    
        return render(request, 'djangoapp/add_review.html', context)

    if request.method == 'POST':

        review = {'name': request.user.first_name + " " + request.user.last_name,
                  'dealership': dealerId,
                  'review': request.POST.get('content')}

        # Build dict
        if request.POST.get('purchase') == 'true':

            review['purchase'] = 'true'

            car = request.POST.get('car')
            car = car.split("/")
            review['car_make'] = car[1]
            review['car_model'] = car[2]
            review['car_year'] = car[0]

            date = datetime.strptime(request.POST.get('date'), "%Y-%m-%d")
            review['purchase_date'] = date.strftime("%m/%d/%Y")
    
        else:

            review['purchase'] = 'false'

            review['car_make'] = ''
            review['car_model'] = ''
            review['car_year'] = ''
            review['purchase_date'] = ''

        review = {"review": review}

        # Post review to CF
        url = "https://6c8c4165.us-east.apigw.appdomain.cloud/dealership/api/review-post"
        response = requests.post(url, json=review)
        status_code = response.status_code

        return redirect("djangoapp:get_dealer_details", dealerId=dealerId)
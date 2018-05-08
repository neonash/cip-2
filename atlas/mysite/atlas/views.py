from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.http import HttpRequest
import json
from classes.error import Error
from atlas import static_data
from atlas.services import product_service
# import pymongo
import traceback
from django.views.decorators.csrf import        ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
#from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from atlas.forms import PasswordResetForm
from atlas.forms import SignUpForm
from atlas.config import dbConfig
import pandas as pd


@login_required(login_url="/login/")
def index(request):
    return render(request, 'atlas/Search.html')


def home(request):
    return render(request, 'atlas/home.html')


def requests(request):
    return render(request, 'atlas/Requests.html')


def sentiment(request):
    return render(request, 'atlas/Sentiment.html')


def summary(request):
    return render(request, 'atlas/Summary.html')


def analysis(request):
    return render(request, 'atlas/Analysis.html')


def topicmodeling(request):
    print("inside view.topicmodeling")
    query = request.GET['request']
    try:
        if query.index('.csv'):
            query = str(query).split('.')[0]
            print(query)
    except:
        print(query)

    try:
        return render(request, 'atlas/Topic.html', {'product': str("atlas/includes/" + query + ".html")})
    except:
        print(traceback.print_exc())
        return render(request, 'atlas/Topic.html', {'product': str("atlas/includes/error.html")})


def clustering(request):
    #query = request.GET['request']
    return render(request, 'atlas/Clustering.html')


def comparison(request):
    #query = request.GET['request']
    return render(request, 'atlas/Comparison.html')


def trigdriv(request):
    return render(request, 'atlas/Trigger_Driver.html')


def upload(request):
    return render(request, 'atlas/Upload.html')


# @require_http_methods(["GET"])
def searchQuery(request):
    # db = pymongo.MongoClient().atlas
    #
    # query = request.GET['query']
    # result = [doc for doc in db.data.find({"Product": query})]
    #
    # if result:
    #     return HttpResponse(json.dumps(result[0]), status=200)
    # else:
    #     # error = Error("product you are looking for does not exist", 404)
    #     # print(error)
    #     print("Error")
    #     return HttpResponse("Product you are looking for does not exist", status=404)
    print(request)
    req_file = dbConfig.dict["requestUrl"]
    req_df = pd.read_csv(req_file)
    for i, r in req_df.iterrows():
        if request.GET['query'] == r['reqKw']:
            return HttpResponse(r['reqKw'], status=200)
            break;
        else:
            return HttpResponse("Product you are looking for does not exist", status=404)
    #return HttpResponse("returning from searchQuery", status=200)

'''
def searchQuery(request):
    query = request.GET['query']
    # print(static_data.products[query])

    if query in static_data.products:
        return HttpResponse(json.dumps(static_data.products[query]), status=200)
    else:
        # error = Error("product you are looking for does not exist", 404)
        # print(error)
        print("error")
        return HttpResponse("Product you are looking for does not exist", status=404)
'''


@csrf_exempt
def uploadFile(request):
    print("inside uploadFile")
    print (request)
    # print dir(request)
    # print(type(request._files['upload'].file))
    responseObject = product_service.uploadFile(request)  # response object contains table_data

    # form = cgi.FieldStorage()
    # return HttpResponse(json.dumps([responseObject, table_data_df]), status=responseObject["status"])
    return HttpResponse(json.dumps([responseObject]), status=responseObject["status"])


def start_analysis(self):
    print("inside start_analysis")
    responseObject = product_service.start_analysis()

    return HttpResponse(json.dumps([responseObject]), status=responseObject["status"])


def read_dims(request):
    print("inside readdims")
    print (request)
    #print dir(request)
    responseObject = product_service.read_dims(request)  # response object contains table_data
    print(responseObject)
    print(type(responseObject))
    return HttpResponse(json.dumps(responseObject), status=200)


def addProduct(request):
    #    return HttpResponse("added", status=200)
    JSONdata = request.POST['name']
    print("Views -> add product request = ", JSONdata)
    site_data = request.POST['site']
    #site_data = request.POST.get('site', False)
    print("Views -> add product site = ", site_data)
    print(json.loads(site_data))
    responseObject = product_service.raiseRequest(JSONdata, json.loads(site_data), False)
    return HttpResponse(json.dumps(responseObject), status=responseObject["status"])


def getRequests(request):
    print(product_service.fetchRequests())
    return HttpResponse(product_service.fetchRequests(), status=200)


def refreshProduct(request, product_name):
    #return HttpResponse("refreshed", status=200)
    # JSONdata = request.PUT['name']
    responseObject = product_service.raiseRequest(product_name, True)
    print("Views -> refresh product request = ", product_name)
    return HttpResponse(json.dumps(responseObject), status=responseObject["status"])


# @require_http_methods(["POST"])
# def searchQuery(request):
#     print("PUT")
#     return
#
#
# @require_http_methods(["PUT"])
# def searchQuery(request):
#     print("PUT")
#     return

def getAutoCompleteList(request):
    #return HttpResponse(json.dumps({'dict_data': static_data.product}))
    return HttpResponse(json.dumps(product_service.getMetaDataFromProducts()), status=200)


def password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
    else:
        form = PasswordResetForm()
    return render(request, 'registration/password_reset_form.html', {'form': form})


def password_reset_done(request):
    return render(request, 'registration/password_reset_done.html')


def password_reset_confirm(request):
    return render(request, 'registration/password_reset_confirm.html')


def password_reset_complete(request):
    return render(request, 'registration/password_reset_complete.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

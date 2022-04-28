from typing import List
from django.http import HttpRequest, QueryDict
from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch, QuerySet
from .models import Product
from .forms import ProductFilterForm
from django.contrib.sessions.backends.base import SessionBase

def update_state(params:QueryDict, session:SessionBase):
    if params.get('reset'):
        session.clear()
    
    if params.get('sort'):
        session['sort'] = 'minimum_age_appropriate' if params.get('sort') == 'age' else params.get('sort')
    
    if(params.get('name_search')):
        session['name_search'] = params.get('name_search')
    
    if(params.get('min_price')):
        session['min_price'] = params.get('min_price')

    if(params.get('max_price')):
        session['max_price'] = params.get('max_price')

    print(dict(session)) # Print current state of session for debugging

def index(request:HttpRequest):
    get_params = request.GET
    session = request.session
    form = ProductFilterForm(get_params)
    update_state(get_params,session)

    products:List[Product] = Product.objects.all().order_by(session.get('sort','name'))
    
    name_search = session.get('name_search')
    min_price = session.get('min_price')
    max_price = session.get('max_price')

    if name_search:
        products = products.filter(name__icontains=name_search)
    
    if min_price:
        products = products.filter(price__gte=min_price)
    
    if max_price:
        products = products.filter(price__lte=max_price)
    
    Product.objects.prefetch_related(Prefetch('productimage_set'))
    
    context = {'products': products, 'form': form}
    return render(request, 'products/index.html', context)

def show(request, product_id):
    p = get_object_or_404(Product, pk=product_id)

    images:QuerySet = p.productimage_set.all()

    context = { 'product':p, 'images': images if images.exists() else None }
    return render(request, 'products/show.html', context)
    

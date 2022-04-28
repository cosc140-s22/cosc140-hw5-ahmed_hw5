from typing import List
from django.http import HttpRequest, QueryDict
from django.shortcuts import redirect, render, get_object_or_404
from django.db.models import Prefetch, QuerySet
from django.contrib.sessions.backends.base import SessionBase
from django.urls import reverse

from .models import Product
from .forms import ProductFilterForm


def get_query(session:SessionBase):
    query_string = [F"{key}={session.get(key)}" for key in session.keys()]
    return '&'.join(query_string)


def update_state(params:QueryDict, session:SessionBase, keys):
    if params.get('reset'):
        session.clear()
    
    for key in keys:
        if params.get(key):
            session[key] = params.get(key)
    
def index(request:HttpRequest):
    params = request.GET
    session = request.session
    form = ProductFilterForm(params)

    search_sort_keys = ['sort','name_search','min_price','max_price']
    update_state(params,session, search_sort_keys)
    
    for key in search_sort_keys:
        '''
            Redirect to url with query string that includes all search/sort parameters applied
        '''
        if key in session.keys() and key not in params.keys():
            return redirect(F"{reverse('index')}?{get_query(session)}")

    products:List[Product] = Product.objects.all().order_by('minimum_age_appropriate' if params.get('sort')=='age' else params.get('sort','name'))

    name_search = params.get('name_search')
    min_price = params.get('min_price')
    max_price = params.get('max_price')

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
    

from typing import List
from django.http import HttpRequest, QueryDict
from django.shortcuts import redirect, render, get_object_or_404
from django.db.models import Prefetch, QuerySet
from django.contrib.sessions.backends.base import SessionBase
from django.urls import reverse

from .models import Product
from .forms import ProductFilterForm


def get_query(session:SessionBase):
    query_string = []
    for key in session.keys():
        val = 'age' if session.get(key) == 'minimum_age_appropriate' else session.get(key)
        query_string.append(F"{key}={val}")
    return '&'.join(query_string)


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
    
def index(request:HttpRequest):
    get_params = request.GET
    session = request.session
    form = ProductFilterForm(get_params)
    update_state(get_params,session)

    for key in ['sort','name_search','min_price','max_price']:
        '''
            Redirect to url with query string that includes all search/sort parameters applied
        '''
        if key in session.keys() and key not in get_params.keys():
            return redirect(F"{reverse('index')}?{get_query(session)}")

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
    print(dict(session))
    return render(request, 'products/index.html', context)

def show(request, product_id):
    p = get_object_or_404(Product, pk=product_id)

    images:QuerySet = p.productimage_set.all()

    context = { 'product':p, 'images': images if images.exists() else None }
    return render(request, 'products/show.html', context)
    

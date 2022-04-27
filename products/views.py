from typing import List
from django.http import HttpRequest
from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch, QuerySet
from .models import Product
from .forms import ProductFilterForm

def index(request:HttpRequest):
    get_params = request.GET
    form = ProductFilterForm(get_params)
    
    sort_by = get_params.get('sort','name')
    sort_by = 'minimum_age_appropriate' if sort_by == 'age' else sort_by
    
    name_search = get_params.get('name_search')
    min_price = get_params.get('min_price')
    max_price = get_params.get('max_price')

    products:List[Product] = Product.objects.all().order_by(sort_by)

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
    

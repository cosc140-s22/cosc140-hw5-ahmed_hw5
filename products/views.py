from genericpath import exists
from typing import List
from django.http import HttpRequest
from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch, QuerySet
from .models import Product
from .forms import ProductFilterForm

def index(request:HttpRequest):
    get_params = request.GET
    order_index = get_params.get('sort','name')
    order_index = 'minimum_age_appropriate' if order_index == 'age' else order_index
    products:List[Product] = Product.objects.all().order_by(order_index)
    form = ProductFilterForm(request.GET)
    name_search = request.GET.get('name_search')
    
    if name_search:
        products = products.filter(name__icontains=name_search)
    
    Product.objects.prefetch_related(Prefetch('productimage_set'))

    product_images = [p.random_image() for p in products]
    
    context = {'products': zip(products, product_images), 'form': form}
    
    return render(request, 'products/index.html', context)

def show(request, product_id):
    p = get_object_or_404(Product, pk=product_id)

    images:QuerySet = p.productimage_set.all()

    context = { 'product':p, 'images': images if images.exists() else None }
    return render(request, 'products/show.html', context)
    

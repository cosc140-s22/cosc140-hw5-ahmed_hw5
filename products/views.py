from genericpath import exists
from typing import List
from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch, QuerySet
from .models import Product
from .forms import ProductFilterForm

def index(request):
    products:List[Product] = Product.objects.all().order_by('name')
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
    

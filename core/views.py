from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Product


@login_required
def home(request):
    products = Product.objects.all()
    return render(request, 'core/home.html', {'products': products})


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'core/product_detail.html', {'product': product})

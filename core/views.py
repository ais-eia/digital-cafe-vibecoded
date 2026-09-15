from django.db import transaction
from django.db.models import F
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AddToCartForm
from .models import CartItem, Product


@login_required
def home(request):
    products = Product.objects.all()
    return render(request, 'core/home.html', {'products': products})


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = AddToCartForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        quantity = form.cleaned_data['quantity']
        with transaction.atomic():
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={'quantity': quantity},
            )
            if not created:
                if cart_item.quantity + quantity > 99:
                    form.add_error(
                        'quantity',
                        'The total quantity for a product cannot exceed 99.',
                    )
                    return render(
                        request,
                        'core/product_detail.html',
                        {'product': product, 'form': form},
                    )
                cart_item.quantity = F('quantity') + quantity
                cart_item.save(update_fields=['quantity'])
                cart_item.refresh_from_db()
        return redirect('cart')
    return render(request, 'core/product_detail.html', {'product': product, 'form': form})


@login_required
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    return render(request, 'core/cart.html', {'cart_items': cart_items})

from django.db import transaction
from django.db.models import F
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .forms import AddToCartForm, CheckoutItemForm
from .models import CartItem, Product, Transaction, TransactionLineItem
from .utils import redirect_without_script_prefix


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
        return redirect_without_script_prefix('cart')
    return render(request, 'core/product_detail.html', {'product': product, 'form': form})


@login_required
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    return render(request, 'core/cart.html', {'cart_items': cart_items})


def _checkout_context(cart_items, forms=None):
    forms = forms or {
        item.pk: CheckoutItemForm(initial={'quantity': item.quantity})
        for item in cart_items
    }
    return {
        'checkout_rows': [
            {'item': item, 'form': forms[item.pk]}
            for item in cart_items
        ],
        'total': sum((item.line_total for item in cart_items), 0),
    }


@login_required
def checkout(request):
    cart_items = list(
        CartItem.objects.filter(user=request.user).select_related('product')
    )
    if request.method == 'POST':
        action = request.POST.get('action', '')
        item_id = request.POST.get('item_id')
        if action == 'remove' and item_id:
            CartItem.objects.filter(user=request.user, pk=item_id).delete()
            return redirect_without_script_prefix('checkout')
        if action == 'update' and item_id:
            item = get_object_or_404(CartItem, user=request.user, pk=item_id)
            item_form = CheckoutItemForm(request.POST)
            if item_form.is_valid():
                item.quantity = item_form.cleaned_data['quantity']
                item.save(update_fields=['quantity'])
                return redirect_without_script_prefix('checkout')
            forms = {
                cart_item.pk: CheckoutItemForm(initial={'quantity': cart_item.quantity})
                for cart_item in cart_items
            }
            forms[item.pk] = item_form
            return render(
                request,
                'core/checkout.html',
                _checkout_context(cart_items, forms),
            )
        if action == 'complete':
            with transaction.atomic():
                current_items = list(
                    CartItem.objects.select_for_update()
                    .filter(user=request.user)
                    .select_related('product')
                )
                if not current_items:
                    return render(
                        request,
                        'core/checkout.html',
                        _checkout_context(current_items),
                    )
                total = sum((item.line_total for item in current_items), 0)
                purchase = Transaction.objects.create(user=request.user, total=total)
                TransactionLineItem.objects.bulk_create([
                    TransactionLineItem(
                        transaction=purchase,
                        product=item.product,
                        product_name=item.product.name,
                        unit_price=item.product.price,
                        quantity=item.quantity,
                    )
                    for item in current_items
                ])
                CartItem.objects.filter(user=request.user).delete()
            return redirect_without_script_prefix('checkout-complete', transaction_id=purchase.pk)
    return render(request, 'core/checkout.html', _checkout_context(cart_items))


@login_required
def checkout_complete(request, transaction_id):
    purchase = get_object_or_404(Transaction, pk=transaction_id, user=request.user)
    return render(request, 'core/checkout_complete.html', {'purchase': purchase})


@login_required
def transaction_history(request):
    transactions = (
        Transaction.objects.filter(user=request.user)
        .prefetch_related('line_items')
    )
    return render(
        request,
        'core/transaction_history.html',
        {'transactions': transactions},
    )

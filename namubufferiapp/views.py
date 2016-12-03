from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string

from forms import MoneyForm
from models import Account, Product, Category, Transaction


@login_required(redirect_field_name=None)
def home(request):
    if request.user.is_superuser:
        return render(request, 'namubufferiapp/base_admin.html')

    # If the user is a new one and doesn't have an account, create one for her
    if not hasattr(request.user, 'account'):
        new_account = Account(user=request.user)
        new_account.save()

    context = dict(money_form=MoneyForm(),
                   products=Product.objects.all(),
                   categories=Category.objects.all(),
                   transactions=request.user.account.transaction_set.all())
    return render(request, 'namubufferiapp/base_home.html', context)


@login_required(redirect_field_name=None)
def buy(request):
    if request.user.is_superuser:
        return render(request, 'namubufferiapp/base_admin.html')

    if request.method == 'POST':
        product = get_object_or_404(Product, pk=request.POST['product_key'])
        price = product.price
        request.user.account.make_payment(price)

        new_transaction = Transaction()
        new_transaction.customer = request.user.account
        new_transaction.amount = -price
        new_transaction.product = product
        new_transaction.save()

        product.make_sale()

        return JsonResponse({'balance': request.user.account.balance,
                             'transactionkey': new_transaction.pk,
                             'modalMessage': "Purchase Successful",
                             'message': render_to_string('namubufferiapp/message.html',
                                                         {'message': "Purchase Successful"}),
                             })
    else:
        raise Http404()


@login_required(redirect_field_name=None)
def deposit(request):
    if request.user.is_superuser:
        return render(request, 'namubufferiapp/base_admin.html')

    if request.method == 'POST':
        money_form = MoneyForm(request.POST)

        if money_form.is_valid():
            euros = request.POST['euros']
            cents = request.POST['cents']
            amount = Decimal(euros) + Decimal(cents)/100

            request.user.account.make_deposit(amount)

            new_transaction = Transaction()
            new_transaction.customer = request.user.account
            new_transaction.amount = amount
            new_transaction.save()

            return JsonResponse({'balance': request.user.account.balance,
                                 'transactionkey': new_transaction.pk,
                                 'modalMessage': "Deposit Successful",
                                 'message': render_to_string('namubufferiapp/message.html',
                                                             {'message': "Deposit Successful",
                                                              'transaction': new_transaction,
                                                              }),
                                 })
        else:
            # https://docs.djangoproject.com/en/1.10/ref/forms/api/#django.forms.Form.errors.as_json
            # https://docs.djangoproject.com/ja/1.9/ref/request-response/#jsonresponse-objects
            #return JsonResponse({"errors": + money_form.errors.as_json()})
            # FTS...
            return HttpResponse('{"errors":' + money_form.errors.as_json() + '}', content_type="application/json")
    else:
        raise Http404()


@login_required(redirect_field_name=None)
def transaction_history(request):
    if request.user.is_superuser:
        return render(request, 'namubufferiapp/base_admin.html')

    return JsonResponse({'transactionhistory': render_to_string('namubufferiapp/transactionhistory.html',
                                                                {'transactions': request.user.account.transaction_set.all()[:5]})
                         })


@login_required(redirect_field_name=None)
def receipt(request):
    if request.user.is_superuser:
        return render(request, 'namubufferiapp/base_admin.html')

    if request.method == 'POST':
        transaction = get_object_or_404(request.user.account.transaction_set.all(),
                                        pk=request.POST['transaction_key'])

        receipt = {'customer': transaction.customer.user.username,
                   'amount': transaction.amount,
                   'timestamp': transaction.timestamp,
                   'transactionkey': transaction.pk,
                   'canceled': transaction.canceled,
                   }
        try:
            receipt['product'] = transaction.product.name
        except:
            receipt['product'] = 'Deposit'

        return JsonResponse({'receipt': receipt})

    else:
        raise Http404()


@login_required(redirect_field_name=None)
def cancel_transaction(request):
    if request.user.is_superuser:
        return render(request, 'namubufferiapp/base_admin.html')

    if request.method == 'POST':
        transaction = get_object_or_404(request.user.account.transaction_set.all(),
                                        pk=request.POST['transaction_key'])

        if (request.user == transaction.customer.user and not transaction.canceled):
            transaction.cancel()

            return JsonResponse({'balance': request.user.account.balance,
                                 'modalMessage': "Transaction Canceled",
                                 'message': render_to_string('namubufferiapp/message.html',
                                                             {'message': "Transaction Canceled",
                                                              'transaction': transaction})
                                 })
        else:
            return HttpResponse(status=204)
    else:
        raise Http404()


def register(request):
    """
    Check for further dev:
    http://www.djangobook.com/en/2.0/chapter14.html
    http://ipasic.com/article/user-registration-and-email-confirmation-django/
    https://docs.djangoproject.com/en/1.7/topics/email/

    """

    if request.method == 'POST':
        register_form = UserCreationForm(request.POST)
        if register_form.is_valid():
            print request.POST
            new_user = register_form.save()

            new_account = Account()
            new_account.user = new_user
            new_account.save()

            return JsonResponse({'modalMessage': "Register Success. You can now sign in.",
                                 'message': render_to_string('namubufferiapp/message.html',
                                                             {'message': "Register Success. You can now sign in."})
                                 })
        else:
            return HttpResponse('{"errors":' + register_form.errors.as_json() + '}', content_type="application/json")

    else:
        raise Http404()

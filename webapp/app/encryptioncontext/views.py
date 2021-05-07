import logging
logger = logging.getLogger(__name__)

from django.shortcuts import render
from django.http import HttpResponseRedirect

from .forms import CustomerProfileForm
from .models import CustomerProfile

import json

# Create your views here.
def index(request):
    context={}
    return render(request,'create',context)

def create(request):
    if request.method =='GET':
        form=CustomerProfileForm()
        context={'form': form}
        return render(request, 'create.html', context)

    if request.method=='POST':
        form = CustomerProfileForm(request.POST)
        if not form.is_valid():
            #form error
            context={'form': form}
            return render(request, 'create.html', context)
        elif CustomerProfile.objects.filter(account_number=form.cleaned_data['account_number']).first():
            #account number exists
            form.add_error('account_number',"Account Number already exists")
            context={'form': form}
            return render(request, 'create.html', context)
        else:
            acct=CustomerProfile(account_number=form.cleaned_data['account_number'],userid=form.cleaned_data['userid'])
            #acct.userid="" #clear out, production app wouldn't have this field in the database schema
            acct.save()
            return HttpResponseRedirect( 'authenticate' )

def authenticate(request):
    if request.method == 'POST':
        form = CustomerProfileForm(request.POST)
        if not form.is_valid():
            context={'form':form}
            return render(request,"authenticate.html",context)
        else:
            acct=CustomerProfile(account_number=form.cleaned_data['account_number'],userid=form.cleaned_data['userid'])
            try:
                account_in_db=CustomerProfile.objects.get(account_number=acct.account_number)
            except CustomerProfile.DoesNotExist:
                form.add_error('account_number',"Invalid Account Number")
                context={'form':form}
                return render(request,"authenticate.html",context)
            else:
                userid=account_in_db.userid
                if acct.userid==userid:
                    return render(request,'authenticatesuccess.html',{})
                else:
                    form.add_error('account_number',"Account number entered incorrectly")
                    context={'form':form}
                    return render(request,"authenticate.html",context)

    if request.method=='GET':
        form=CustomerProfileForm()
        context={'form':form}
        return render(request,"authenticate.html",context)


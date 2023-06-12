from django import forms
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
import xlrd
from .forms import UploadFileForm
from .models import UploadedFile
import pandas as pd

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # پردازش فایل آپلود شده
            df = handle_uploaded_file(request.FILES['file'])
            table_html = df.to_html()
            return render(request, 'show_data.html', {'table_html': table_html})
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})

from django.http import HttpResponse
from django.shortcuts import render
import requests
import pandas as pd

def show_data(request):
    # فرض میکنیم که df یک DataFrame حاوی داده‌هایی است که میخواهیم نمایش دهیم
    df = ...
    
    # تبدیل DataFrame به جدول HTML
    table_html = df.to_html()
    
    # ارسال جدول HTML به قالب صفحه وب
    return render(request, 'show_data.html', {'table_html': table_html})




# def get_price(coin, date):
#     # دریافت داده‌ها از CoinMarketCap
#     response = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest', headers={'X-CMC_PRO_API_KEY': 'b6311d60-249a-4856-8fe6-3d2b93c04d76'})

#     # تبدیل داده‌های JSON به DataFrame
#     data = response.json()['data']
#     df = pd.DataFrame(data)

#     # فیلتر کردن ستون‌های مورد نظر
#     df = df[['name', 'quote']]
#     df['price'] = df['quote'].apply(lambda x: x['USD']['price'])
#     df['last_updated'] = df['quote'].apply(lambda x: x['USD']['last_updated'])
#     df = df[['name', 'price', 'last_updated']]

#     # جستجو برای پیدا کردن قیمت ارز در تاریخ مشخص شده
#     coin_row = df.loc[df['name'] == coin]
#     if coin_row.empty:
#         return f"{coin} not found"
#     else:
#         price = coin_row.iloc[0]['price']
#         last_updated = coin_row.iloc[0]['last_updated']
#         if date == last_updated:
#             return f"The price of {coin} on {date} was {price}"
#         else:
#             return f"No data found for {coin} on {date}" 


import requests
import pandas as pd

def get_price(coin, date):
    # تبدیل نام ارز به حروف کوچک
    coin = coin.lower()
    
    # دریافت داده‌ها از CoinGecko
    response = requests.get(f'https://api.coingecko.com/api/v3/coins/{coin}/history?date={date}')
    
    # بررسی وضعیت پاسخ
    if response.status_code == 200:
        # تبدیل داده‌های JSON به دیکشنری
        data = response.json()
        
        # بررسی وجود کلید market_data در دیکشنری data
        if 'market_data' in data:
            # استخراج قیمت ارز در تاریخ مشخص شده
            price = data['market_data']['current_price']['usd']
            return f"The price of {coin} on {date} was {price}"
        else:
            return f"No market data found for {coin} on {date}"
    else:
        return f"No data found for {coin} on {date}"


result = get_price('Bitcoin', '03-02-2022')
print(result)


# def handle_uploaded_file(f):
#     uploaded_file = UploadedFile(file=f)
#     uploaded_file.save()
    
#     # خواندن فایل اکسل و تبدیل آن به DataFrame
#     df = pd.read_excel(f)
    
#     # استفاده از تابع get_price برای پیدا کردن قیمت هر ارز در تاریخ مشخص شده
#     df['price'] = df.apply(lambda row: get_price(row['Coin'], row['Date']), axis=1)
    
#     # نمایش DataFrame حاصل
#     print(df)
    
#     return df


def handle_uploaded_file(f):
    uploaded_file = UploadedFile(file=f)
    uploaded_file.save()
    
    # خواندن فایل اکسل و تبدیل آن به DataFrame
    df = pd.read_excel(f)
    
    # تبدیل فرمت تاریخ به شکل مورد نیاز تابع get_price
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y').dt.strftime('%d-%m-%Y')
    
    # استفاده از تابع get_price برای پیدا کردن قیمت هر ارز در تاریخ مشخص شده
    df['Price'] = df.apply(lambda row: get_price(row['Coin'], row['Date']), axis=1)
    
    # نمایش DataFrame حاصل
    print(df)
    
    return df





def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('upload')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


class CustomUserCreationForm(forms.ModelForm):
    username = forms.CharField(label='نام کاربری')
    password1 = forms.CharField(
        label='رمز عبور', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='تایید رمز عبور', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username',)

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password1'] != cd['password2']:
            raise forms.ValidationError('رمز عبور با تایید آن مطابقت ندارد')
        if len(cd['password1']) < 8:
            raise forms.ValidationError('رمز عبور باید حداقل 8 کاراکتر باشد')
        return cd['password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

def home_view(request):
 return render(request, 'home.html')



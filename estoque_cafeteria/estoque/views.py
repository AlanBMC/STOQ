from django.shortcuts import render

# Create your views here.
def login(request):
    return render(request,  'login.html')

def produtoview(request):
    return render(request, 'produtoview.html')

def estoqueview(request):
    return render(request, 'estoque.html')

def offline(request):
    return render(request, 'offline.html')
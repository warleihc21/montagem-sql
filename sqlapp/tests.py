from django.test import TestCase
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.messages import constants
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
import pandas as pd



#teste de codificação
tabela = pd.read_csv(r"C:\Users\junio\Downloads\TESTES SQL\TESTES SQL\BRADESCO\2642 BRADESCO 15062022(Bloqueado).csv", encoding='iso-8859-1', sep=";")

tabela['VALOR BRUTO'] = tabela['VALOR BRUTO'].replace('.', ',')
tabela['VALOR LIQUIDO'] = tabela['VALOR LIQUIDO'].replace('.', ',')
tabela['VALOR LANÇAMENTO'] = tabela['VALOR LANÇAMENTO'].replace('.', ',')


tabela.to_csv(r"C:\Users\junio\Downloads\2642 BRADESCO 15062022(Bloqueado).csv", index=False)

print(tabela)

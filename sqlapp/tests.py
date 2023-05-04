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
import os



#teste de codificação
tabela = pd.read_csv(r"C:\Users\junio\Downloads\TESTES SQL\TESTES SQL\BRADESCO\2642 BRADESCO 15062022(Bloqueado).csv", encoding='iso-8859-1', sep=";")

# substituir ponto por vírgula e formatar colunas como moeda
tabela['VALOR BRUTO'] = tabela['VALOR BRUTO'].apply(lambda x: f'R$ {x:.2f}'.replace('.', ','))
tabela['VALOR LIQUIDO'] = tabela['VALOR LIQUIDO'].apply(lambda x: f'R$ {x:.2f}'.replace('.', ','))
tabela['VALOR LANÇAMENTO'] = tabela['VALOR LANÇAMENTO'].apply(lambda x: f'R$ {x:.2f}'.replace('.', ','))

# Extrair o código do arquivo
nome_arquivo = os.path.basename(r"C:\Users\junio\Downloads\TESTES SQL\TESTES SQL\BRADESCO\2642 BRADESCO 15062022(Bloqueado).csv")
codigo = nome_arquivo.split()[0]

# Preencher células vazias com o código do arquivo
tabela["CODIGO PROMOTORA PRODUTORA"].fillna(codigo, inplace=True)



tabela.to_csv(r"C:\Users\junio\Downloads\2642 BRADESCO 15062022(Bloqueado).csv", index=False, sep=";", encoding='utf-8-sig')

print(tabela)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.messages import constants
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
import pandas as pd
from tkinter import filedialog
import tkinter as Tk
from .forms import CsvUploadForm
from .models import CsvData
from django.core.files.storage import FileSystemStorage




@login_required(login_url='/auth/logar/')
def index(request):    
    return render(request, 'index.html')


@login_required(login_url='/auth/logar/')
def upload_csv(request):
    form = CsvUploadForm()
    if request.method == 'POST':
        form = CsvUploadForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    return render(request, 'upload.html', {'form': form})


@login_required(login_url='/auth/logar/')
def home(request):
    data = CsvData.objects.all()
    return render(request, 'home.html', {'data': data})




@login_required(login_url='/auth/logar/')
def safra(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        tabela = pd.read_csv(file, sep=';')

        tabela.insert(loc=31, column='Natureza', value=0)
        tabela.insert(loc=32, column='Tipo', value=0)
        celulas_vazias = tabela.isnull()
        somente_vazias = tabela[tabela['Nome Subcorban'].isnull()]

        somente_vazias.loc[tabela['Tp Pagamento Bruto Comissao'] == 'A VISTA', 'Natureza'] = 'CREDITO A VISTA'
        somente_vazias.loc[tabela['Tp Pagamento Bruto Comissao'] == 'A VISTA FGTS', 'Natureza'] = 'CREDITO A VISTA'
        somente_vazias.loc[tabela['Tp Pagamento Bruto Comissao'] == 'SERVICO', 'Natureza'] = 'CREDITO DIFERIDO'

        somente_vazias.loc[tabela['Tp Pagamento Bruto Comissao'] == 'A VISTA', 'Tipo'] = 'A VISTA'
        somente_vazias.loc[tabela['Tp Pagamento Bruto Comissao'] == 'A VISTA FGTS', 'Tipo'] = 'A VISTA'
        somente_vazias.loc[tabela['Tp Pagamento Bruto Comissao'] == 'SERVICO', 'Tipo'] = 'DIFERIDO'

        # Seleciona somente as colunas desejadas
        somente_vazias = somente_vazias[['Contrato', 'CPF', 'Nome Cliente', 'Natureza', 'Tipo',
                                         'Tp Pagamento Bruto Comissao', 'Valor Principal', 'Vl Troco',
                                         'Vl Pagamento Bruto Comissao', 'Pc Comissao a vista',
                                         'Data Pagamento Comissao']]

        # Salva os dados no banco de dados
        for index, row in somente_vazias.iterrows():
            CsvData.objects.create(
                proposta=row['Contrato'],
                cpf=row['CPF'],
                nome=row['Nome Cliente'],
                natureza_do_lancamento=row['Natureza'],
                tipo_de_lancamento=row['Tipo'],
                observacao=row['Tp Pagamento Bruto Comissao'],
                bruto_contrato=row['Valor Principal'],
                liquido_contrato=row['Vl Troco'],
                vlr_lancamento=row['Vl Pagamento Bruto Comissao'],
                percentual_lancamento=row['Pc Comissao a vista'],
                data_do_lancamento =row['Data Pagamento Comissao']
            )

        # Salva o arquivo processado no sistema de arquivos do servidor
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        somente_vazias.to_csv(filename, index=False)

        messages.add_message(request, constants.SUCCESS, 'Arquivo processado com sucesso!')

    return render(request, 'safra.html')



@login_required(login_url='/auth/logar/')
def bradesco(request):
    if request.method == 'POST' and request.FILES['file']:
        with open('file', encoding='iso-8859-1') as f:
            tabela = pd.read_csv(f, sep=';')

        # Substituir pontos por vírgulas nas colunas 'VALOR BRUTO', 'VALOR LIQUIDO' e 'VALOR LANCAMENTO'
        tabela['VALOR BRUTO'] = tabela['VALOR BRUTO'].str.replace('.', ',')
        tabela['VALOR LIQUIDO'] = tabela['VALOR LIQUIDO'].str.replace('.', ',')
        tabela['VALOR LANÇAMENTO'] = tabela['VALOR LANÇAMENTO'].str.replace('.', ',')

        # Salvar o arquivo processado
        filenamessave = filedialog.asksaveasfilename(
                        filetypes=(
                            ("Arquivos csv", "*.csv"),
                            ("Todos os arquivos", "*.*"),
                        )
                    )
        tabela.to_csv(filenamessave, index=False)

        # Exibir mensagem de sucesso
        messages.add_message(request, constants.SUCCESS, 'Arquivo processado com sucesso!')

    return render(request, 'bradesco.html')





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
from datetime import datetime




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
    layouts = ['CONSIGNADO', 'Layout 2', 'Layout 3']  # Adicione aqui os diferentes layouts disponíveis
    if request.method == 'POST' and request.FILES['file']:
        layout = request.POST['layout']  # Obtém o layout selecionado pelo usuário
        file = request.FILES['file']

        if layout == 'CONSIGNADO':
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
                    banco='SAFRA',
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

        #elif layout == 'Layout 2':
            # Alterações específicas para o Layout 2
        #elif layout == 'Layout 3':
            # Alterações específicas para o Layout 3

    return render(request, 'safra.html', {'layouts': layouts})



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





@login_required(login_url='/auth/logar/')
def filtrar_dados(request):
    if request.method == 'GET':
        banco = request.GET.get('banco')
        layout = request.GET.get('layout')
        proposta = request.GET.get('proposta')
        cpf = request.GET.get('cpf')
        nome = request.GET.get('nome')
        natureza_do_lancamento = request.GET.get('natureza_do_lancamento')
        tipo_de_lancamento = request.GET.get('tipo_de_lancamento')
        observacao = request.GET.get('observacao')
        maior_que = request.GET.get('maior_que')
        menor_que = request.GET.get('menor_que')
        data_proposta_inicio = request.GET.get('data_proposta_inicio')
        data_proposta_final = request.GET.get('data_proposta_final')
        data_lancamento_inicio = request.GET.get('data_lancamento_inicio')
        data_lancamento_final = request.GET.get('data_lancamento_final')
        dados = CsvData.objects.all()

        if banco or layout or proposta or cpf or nome or natureza_do_lancamento or tipo_de_lancamento or observacao or maior_que or menor_que or data_proposta_inicio or data_proposta_final or data_lancamento_inicio or data_lancamento_final:

            if not maior_que:
                maior_que = 0

            if not menor_que:
                menor_que = 999999999999

            if banco:
                dados = dados.filter(banco=banco)

            if layout:
                dados = dados.filter(layout=layout)

            if proposta:
                dados = dados.filter(proposta=proposta)

            if cpf:
                dados = dados.filter(cpf=cpf)

            if nome:
                dados = dados.filter(nome__icontains=nome)

            if natureza_do_lancamento:
                dados = dados.filter(natureza_do_lancamento=natureza_do_lancamento)
            
            if tipo_de_lancamento:
                dados = dados.filter(tipo_de_lancamento=tipo_de_lancamento)

            if observacao:
                dados = dados.filter(observacao__icontains=observacao)

            dados = dados.filter(vlr_lancamento__gte=maior_que).filter(vlr_lancamento__lte=menor_que)

            if data_proposta_inicio and data_proposta_final:
                # Converter as strings em objetos de data
                data_proposta_inicio = datetime.strptime(data_proposta_inicio, '%Y-%m-%d').date()
                data_proposta_final = datetime.strptime(data_proposta_final, '%Y-%m-%d').date()

                # Filtrar os objetos usando a faixa de datas
                objetos_filtrados = CsvData.objects.filter(data__range=(data_proposta_inicio, data_proposta_final))
            else:
                objetos_filtrados = CsvData.objects.all()

            # Passar os objetos filtrados para o contexto e renderizar o template
            context = {
                'objetos_filtrados': objetos_filtrados
            }

    return render(request, 'filtrar_dados.html')



@login_required(login_url='/auth/logar/')
def resultado_filtro(request):

    return render(request, 'resultado_filtro.html')

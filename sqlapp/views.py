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
from .models import CsvData




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





@login_required(login_url='/auth/logar/')
def filtrar_dados(request):
    bancos = CsvData.objects.values_list('banco', flat=True).distinct()
    layouts = CsvData.objects.values_list('layout', flat=True).distinct()
    propostas = CsvData.objects.values_list('proposta', flat=True).distinct()
    cpfs = CsvData.objects.values_list('cpf', flat=True).distinct()
    nomes = CsvData.objects.values_list('nome', flat=True).distinct()
    naturezas = CsvData.objects.values_list('natureza_do_lancamento', flat=True).distinct()
    tipos = CsvData.objects.values_list('tipo_de_lancamento', flat=True).distinct()
    observacoes = CsvData.objects.values_list('observacao', flat=True).distinct()
    valores = CsvData.objects.values_list('vlr_lancamento', flat=True).distinct()
    datas_proposta = CsvData.objects.values_list('data_da_proposta', flat=True).distinct()
    datas_lancamento = CsvData.objects.values_list('data_do_lancamento', flat=True).distinct()

    if request.method == 'POST':
        banco = request.POST.get('banco')
        layout = request.POST.get('layout')
        proposta = request.POST.get('proposta')
        cpf = request.POST.get('cpf')
        nome = request.POST.get('nome')
        natureza = request.POST.get('natureza')
        tipo = request.POST.get('tipo')
        observacao = request.POST.get('observacao')
        valor = request.POST.get('valor')
        data_proposta = request.POST.get('data_proposta')
        data_lancamento = request.POST.get('data_lancamento')

        dados_filtrados = CsvData.objects.filter(
            banco__icontains=banco,
            layout__icontains=layout,
            proposta__icontains=proposta,
            cpf__icontains=cpf,
            nome__icontains=nome,
            natureza_do_lancamento__icontains=natureza,
            tipo_de_lancamento__icontains=tipo,
            observacao__icontains=observacao,
            vlr_lancamento__icontains=valor,
            data_da_proposta__icontains=data_proposta,
            data_do_lancamento__icontains=data_lancamento
        )

        return render(request, 'resultado_filtro.html', {
            'dados_filtrados': dados_filtrados
        })

    return render(request, 'filtrar_dados.html', {
        'bancos': bancos,
        'layouts': layouts,
        'propostas': propostas,
        'cpfs': cpfs,
        'nomes': nomes,
        'naturezas': naturezas,
        'tipos': tipos,
        'observacoes': observacoes,
        'valores': valores,
        'datas_proposta': datas_proposta,
        'datas_lancamento': datas_lancamento
    })



@login_required(login_url='/auth/logar/')
def resultado_filtro(request):    
    return render(request, 'resultado_filtro.html')

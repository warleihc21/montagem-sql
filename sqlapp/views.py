from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages import constants
from django.db.models import Q
import pandas as pd
from .forms import CsvUploadForm
from .models import CsvData
from django.core.files.storage import FileSystemStorage
from tkinter import filedialog


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
                    layout=layout,
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
                    data_do_lancamento=row['Data Pagamento Comissao']
                )

            # Salva o arquivo processado no sistema de arquivos do servidor
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
            somente_vazias.to_csv(filename, index=False)

            messages.add_message(request, constants.SUCCESS, 'Arquivo processado com sucesso!')

        # elif layout == 'Layout 2':
        # Alterações específicas para o Layout 2
        # elif layout == 'Layout 3':
        # Alterações específicas para o Layout 3

    return render(request, 'safra.html', {'layouts': layouts})


@login_required(login_url='/auth/logar/')
def bradesco(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        tabela = pd.read_csv(file, sep=';')

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
    naturezas_do_lancamento = CsvData.objects.values_list('natureza_do_lancamento', flat=True).distinct()
    tipos_de_lancamento = CsvData.objects.values_list('tipo_de_lancamento', flat=True).distinct()
    observacaos = CsvData.objects.values_list('observacao', flat=True).distinct()

    return render(request, 'filtrar_dados.html', {
        'bancos': bancos,
        'layouts': layouts,
        'natureza_do_lancamentos': naturezas_do_lancamento,
        'tipo_de_lancamentos': tipos_de_lancamento,
        'observacaos': observacaos   
    })



@login_required(login_url='/auth/logar/')
def resultado_filtro(request):
    if request.method == 'GET':
        filtros = {}

        banco = request.GET.get('banco')
        if banco:
            filtros['banco__icontains'] = banco

        layout = request.GET.get('layout')
        if layout:
            filtros['layout__icontains'] = layout

        proposta = request.GET.get('proposta')
        if proposta:
            filtros['proposta__icontains'] = proposta

        cpf = request.GET.get('cpf')
        if cpf:
            filtros['cpf__icontains'] = cpf

        nome = request.GET.get('nome')
        if nome:
            filtros['nome__icontains'] = nome

        natureza_do_lancamento = request.GET.get('natureza_do_lancamento')
        if natureza_do_lancamento:
            filtros['natureza_do_lancamento__icontains'] = natureza_do_lancamento

        tipo_de_lancamento = request.GET.get('tipo_de_lancamento')
        if tipo_de_lancamento:
            filtros['tipo_de_lancamento__icontains'] = tipo_de_lancamento

        observacao = request.GET.get('observacao')
        if observacao:
            filtros['observacao__icontains'] = observacao

        vlr_lancamento_maior = request.GET.get('maior_que')
        if vlr_lancamento_maior:
            filtros['vlr_lancamento__gt'] = vlr_lancamento_maior

        vlr_lancamento_menor = request.GET.get('menor_que')
        if vlr_lancamento_menor:
            filtros['vlr_lancamento__lt'] = vlr_lancamento_menor

        data_proposta_inicio = request.GET.get('data_proposta_inicio')
        if data_proposta_inicio:
            filtros['data_da_proposta__gte'] = data_proposta_inicio

        data_proposta_final = request.GET.get('data_proposta_final')
        if data_proposta_final:
            filtros['data_da_proposta__lte'] = data_proposta_final

        data_lancamento_inicio = request.GET.get('data_lancamento_inicio')
        if data_lancamento_inicio:
            filtros['data_do_lancamento__gte'] = data_lancamento_inicio

        data_lancamento_final = request.GET.get('data_lancamento_final')
        if data_lancamento_final:
            filtros['data_do_lancamento__lte'] = data_lancamento_final

        dados_filtrados = CsvData.objects.filter(**filtros)

        if dados_filtrados:
            return render(request, 'resultado_filtro.html', {'dados': dados_filtrados})
        else:
            messages.add_message(request, constants.INFO, 'Nenhum resultado encontrado.')
            return redirect('filtrar_dados')

    return redirect('filtrar_dados')

    
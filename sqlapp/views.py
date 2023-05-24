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

    if request.method == 'GET':
        filtro_banco = request.GET.get('banco')
        filtro_layout = request.GET.get('layout')
        filtro_proposta = request.GET.get('proposta')
        filtro_cpf = request.GET.get('cpf')
        filtro_nome = request.GET.get('nome')
        filtro_natureza_do_lancamento = request.GET.get('natureza_do_lancamento')
        filtro_tipo_de_lancamento = request.GET.get('tipo_de_lancamento')
        filtro_observacao = request.GET.get('observacao')
        filtro_maior_que = request.GET.get('maior_que')
        filtro_menor_que = request.GET.get('menor_que')
        filtro_data_proposta_inicio = request.GET.get('data_proposta_inicio')
        filtro_data_proposta_final = request.GET.get('data_proposta_final')
        filtro_data_lancamento_inicio = request.GET.get('data_lancamento_inicio')
        filtro_data_lancamento_final = request.GET.get('data_lancamento_final')

        # Realizar a filtragem dos dados com base nos parâmetros fornecidos
        data = CsvData.objects.all()

        if filtro_banco:
            data = data.filter(banco=filtro_banco)
        if filtro_layout:
            data = data.filter(layout=filtro_layout)
        if filtro_proposta:
            data = data.filter(proposta=filtro_proposta)
        if filtro_cpf:
            data = data.filter(cpf=filtro_cpf)
        if filtro_nome:
            data = data.filter(nome=filtro_nome)
        if filtro_natureza_do_lancamento:
            data = data.filter(natureza_do_lancamento=filtro_natureza_do_lancamento)
        if filtro_tipo_de_lancamento:
            data = data.filter(tipo_de_lancamento=filtro_tipo_de_lancamento)
        if filtro_observacao:
            data = data.filter(observacao=filtro_observacao)
        if filtro_maior_que:
            data = data.filter(vlr_lancamento__gt=filtro_maior_que)
        if filtro_menor_que:
            data = data.filter(vlr_lancamento__lt=filtro_menor_que)
        if filtro_data_proposta_inicio:
            data = data.filter(data_da_proposta__gte=filtro_data_proposta_inicio)
        if filtro_data_proposta_final:
            data = data.filter(data_da_proposta__lte=filtro_data_proposta_final)
        if filtro_data_lancamento_inicio:
            data = data.filter(data_do_lancamento__gte=filtro_data_lancamento_inicio)
        if filtro_data_lancamento_final:
            data = data.filter(data_do_lancamento__lte=filtro_data_lancamento_final)

        return render(request, 'filtrar_dados.html', {
            'data': data,
            'bancos': bancos,
            'layouts': layouts,
            'natureza_do_lancamentos': naturezas_do_lancamento,
            'tipo_de_lancamentos': tipos_de_lancamento
        })

    return render(request, 'filtrar_dados.html', {
        'bancos': bancos,
        'layouts': layouts,
        'natureza_do_lancamentos': naturezas_do_lancamento,
        'tipo_de_lancamentos': tipos_de_lancamento
    })





@login_required(login_url='/auth/logar/')
def resultado_filtro(request):
    data_param = request.GET.get('data')  # Obtém o parâmetro 'data' da URL

    # Realize as operações desejadas com o parâmetro 'data_param'

    return render(request, 'resultado_filtro.html', {'data_param': data_param})


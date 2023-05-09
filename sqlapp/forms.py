from django import forms
from .models import CsvData

class CsvUploadForm(forms.ModelForm):
    class Meta:
        model = CsvData
        fields = ['banco', 'layout', 'cpf', 'nome', 'natureza_do_lancamento', 'tipo_de_lancamento', 'observacao', 'bruto_contrato', 'liquido_contrato', 'vlr_lancamento', 'percentual_lancamento', 'data_da_proposta', 'data_do_lancamento']


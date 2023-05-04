from django import forms
from .models import CsvData

class CsvUploadForm(forms.ModelForm):
    class Meta:
        model = CsvData
        fields = ['proposta', 'cliente', 'cpf', 'operacao', 'valor_bruto', 'valor_liquido', 'lancamento', 'data_lancamento', 'data_upload',]


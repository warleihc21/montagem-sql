from django.db import models

class CsvData(models.Model):
    proposta = models.CharField(max_length=100)
    cliente = models.CharField(max_length=100)
    cpf = models.CharField(max_length=100)
    operacao = models.CharField(max_length=100)
    valor_bruto = models.CharField(max_length=100)
    valor_liquido = models.CharField(max_length=100)
    lancamento = models.CharField(max_length=100)
    data_lancamento = models.CharField(max_length=100)
    data_upload = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.proposta} - {self.cliente} - {self.cpf} - {self.operacao} - {self.valor_bruto} - {self.valor_liquido} - {self.lancamento} - {self.data_lancamento} - {self.data_upload}"


from django.db import models

class CsvData(models.Model):
    banco = models.CharField(max_length=100)
    layout = models.CharField(max_length=100)
    proposta = models.CharField(max_length=100)
    cpf = models.CharField(max_length=100)
    nome = models.CharField(max_length=100)
    natureza_do_lancamento = models.CharField(max_length=100)
    tipo_de_lancamento = models.CharField(max_length=100)
    observacao = models.CharField(max_length=100)
    bruto_contrato = models.CharField(max_length=100)
    liquido_contrato = models.CharField(max_length=100)
    vlr_lancamento = models.CharField(max_length=100)
    percentual_lancamento = models.CharField(max_length=100)
    data_da_proposta = models.CharField(max_length=100)
    data_do_lancamento = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.banco} - {self.layout} - {self.proposta} - {self.cpf} - {self.nome} - {self.natureza_do_lancamento} - {self.tipo_de_lancamento} - {self.observacao} - {self.bruto_contrato} - {self.liquido_contrato} - {self.vlr_lancamento} - {self.percentual_lancamento} - {self.data_da_proposta} - {self.data_do_lancamento}"



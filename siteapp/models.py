# siteapp/models.py
from django.db import models

class Usuarios(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=120)
    idade = models.PositiveIntegerField()
    email = models.EmailField(blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    cep = models.CharField(max_length=9, blank=True, null=True)
    logradouro = models.CharField(max_length=255, blank=True, null=True)
    bairro = models.CharField(max_length=120, blank=True, null=True)
    cidade = models.CharField(max_length=120, blank=True, null=True)
    uf = models.CharField(max_length=2, blank=True, null=True)

    def __str__(self):
        return f"{self.nome} ({self.id_usuario})"















"""

# siteapp/models.py
from django.db import models

class Usuarios(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255)
    idade = models.IntegerField()
    email = models.EmailField(max_length=254, unique=False, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    cep = models.CharField(max_length=9, blank=True, null=True)  # 00000-000
    logradouro = models.CharField(max_length=255, blank=True, null=True)
    bairro = models.CharField(max_length=120, blank=True, null=True)
    cidade = models.CharField(max_length=120, blank=True, null=True)
    uf = models.CharField(max_length=2, blank=True, null=True)

    def __str__(self):
        return f"{self.nome} ({self.idade} anos)"
        """

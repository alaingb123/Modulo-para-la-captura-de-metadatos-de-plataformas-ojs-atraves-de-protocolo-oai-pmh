from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.core.validators import RegexValidator
# Create your models here.






class Arbitraje(models.Model):
    valor = models.CharField(max_length=255)

    def __str__(self):
        return self.valor

class Pais(models.Model):
    valor = models.CharField(max_length=255)
    def __str__(self):
        return self.valor

class Clasificacion(models.Model):
    valor = models.CharField(max_length=255)
    def __str__(self):
        return self.valor

class Subclasificacion(models.Model):
    clasificacion = models.ForeignKey(Clasificacion, on_delete=models.CASCADE)
    valor = models.CharField(max_length=255)

    def __str__(self):
        return self.valor

class Idioma(models.Model):
    valor = models.CharField(max_length=255)
    def __str__(self):
        return self.valor


class IdiomaR(models.Model):
    valor = models.CharField(max_length=255)
    def __str__(self):
        return self.valor







class Anio(models.Model):
    anio = models.CharField(max_length=100)

    def __str__(self):
        return str(self.anio)


class Volumen(models.Model):
    volumen =  models.CharField(max_length=100)
    anio = models.ForeignKey(Anio, on_delete=models.CASCADE)

    def __str__(self):
        return f"Volumen {self.volumen} - {self.anio}"


class Numero(models.Model):
    numero = models.CharField(max_length=100)
    volumen = models.ForeignKey(Volumen, on_delete=models.CASCADE)

    def __str__(self):
        return f"Número {self.numero} - {self.volumen}"

class Proveedor(models.Model):
    repository_name = models.CharField(max_length=255)
    base_url = models.URLField()
    protocol_version = models.CharField(max_length=10)
    earliest_datestamp = models.DateTimeField()
    deleted_record_policy = models.CharField(max_length=20)
    granularity = models.CharField(max_length=50)

    def __str__(self):
        return self.repository_name
class Set(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    set_spec = models.CharField(max_length=255)
    set_name = models.CharField(max_length=255)



class MetadataFormat(models.Model):
    prefix = models.CharField(max_length=255)
    namespace = models.TextField()
    schema = models.URLField()
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='metadata_formats')

    def __str__(self):
        return self.prefix


class Header(models.Model):
    identifier = models.CharField(max_length=255)
    datestamp = models.DateTimeField()
    set_spec = models.CharField(max_length=255)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)

    def __str__(self):
        return self.identifier

class Autor(models.Model):
    nombre = models.CharField(max_length=255)
    def __str__(self):
        return self.nombre

class ResourceType(models.Model):
    type = models.CharField(max_length=100)








class Article(models.Model):
    header = models.OneToOneField(Header, on_delete=models.CASCADE)
    title = models.TextField()
    creator = ArrayField(models.TextField())
    description = models.TextField()
    publisher = models.TextField()
    date = models.TextField()
    format = models.TextField()
    subject = models.TextField(null=True)
    identifier_url = models.URLField(max_length=1000000)
    source = ArrayField(models.TextField())
    language = models.ForeignKey(Idioma, on_delete=models.SET_NULL, null=True)
    relation = models.URLField(max_length=999999)
    rights = models.TextField()
    resource_types = ArrayField(models.TextField())
    volumen = models.ForeignKey(Volumen, on_delete=models.CASCADE,null= True)
    numero = models.ForeignKey(Numero, on_delete=models.CASCADE,null= True)
    anio = models.ForeignKey(Anio, on_delete=models.CASCADE,null= True)


    def __str__(self):
        creators = ', '.join(self.creator)
        return f"{self.title} by {creators}"

class Revista(models.Model):
    issn_e = models.CharField(max_length=8, validators=[RegexValidator(r'^[0-9]{8}$', 'Ingrese un ISSN válido.')])
    pais = models.ForeignKey(Pais, on_delete=models.SET_NULL, null=True)
    idioma = models.ForeignKey(IdiomaR, on_delete=models.SET_NULL, null=True)
    descripcion = models.TextField()
    editores = models.ManyToManyField('Autor', related_name='editores')
    subclasificacion = models.ManyToManyField(Subclasificacion)
    autores = models.ManyToManyField('Autor', related_name='autores')
    arbitraje = models.ForeignKey(Arbitraje, on_delete=models.SET_NULL, null=True)
    proveedor = models.OneToOneField(Proveedor, on_delete=models.CASCADE)

    def __str__(self):
        return self.proveedor.repository_name


class Articulos_a_actualizar (models.Model):
    id = models.IntegerField(unique=True,primary_key=True)




from django.contrib.auth.models import User

from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from oaipmh.client import Client
from oaipmh.error import XMLSyntaxError

from oaipmh.metadata import MetadataRegistry, oai_dc_reader

from usuario.decorator import role_required
from .forms import CosecharForm, ModificarArticuloForm
from .models import Article, Header, Idioma, Anio, Volumen, Numero, Proveedor, Set, Revista, Pais, IdiomaR, \
    Arbitraje
from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
import urllib.error
from datetime import datetime, time, date
from oaipmh.error import NoRecordsMatchError, BadArgumentError, \
    BadResumptionTokenError, CannotDisseminateFormatError, NoSetHierarchyError
from django.urls import reverse
from .viewR import alphanumeric_key

import requests


def ver_articulo(request, articulo_id):
    articulo = get_object_or_404(Article, id=articulo_id)

    #Estripar descripcion ------------------------------------------------------------------------------------
    #------------------------------------------------------------------------------------------------------------
    try:
        articulo.description = articulo.description.strip('[]')
        articulo.description = articulo.description.strip("'")
        partes = articulo.description.split("', '")
        articulo.description = partes[1]
    except:
        pass




    # ---------------------------------------------------------------------------------------------------------


    # Estripar publisher ------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------
    try:
        articulo.publisher=articulo.publisher.strip('[]')
        articulo.publisher=articulo.publisher.strip("'")
    except:
        pass
    # ---------------------------------------------------------------------------------------------------------

    # Estripar date ------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------

    articulo.date = articulo.date.strip('[]')
    articulo.date = articulo.date.strip("'")

    # ---------------------------------------------------------------------------------------------------------

    # Estripar format ------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------

    articulo.format = articulo.format.strip('[]')
    articulo.format = articulo.format.strip("'")

    # --------------------------------------------------------------------------------------------------------

    # Estripar url ------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------

    articulo.identifier_url = articulo.identifier_url.strip('[]')
    articulo.identifier_url = articulo.identifier_url.strip("'")

    # --------------------------------------------------------------------------------------------------------

    # Estripar lenaguaje ------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------

    articulo.language.valor=estripar_idioma(articulo)

    # --------------------------------------------------------------------------------------------------------

    # Estripar relation ------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------

    articulo.relation = articulo.relation.strip('[]')
    articulo.relation = articulo.relation.strip("'")

    # --------------------------------------------------------------------------------------------------------

    # Estripar relation ------------------------------------------------------------------------------------
    # -----------------------------------------------------------------------------------------------------------

    articulo.rights = articulo.rights.strip('[]')
    articulo.rights = articulo.rights.strip("'")

    # --------------------------------------------------------------------------------------------------------

    return render(request, 'ver_articulo.html', {'articulo': articulo})


def estripar_idioma(articulo):
    articulo.language.valor = articulo.language.valor.strip('[]')
    articulo.language.valor = articulo.language.valor.strip("'")
    return articulo.language.valor


def estripar_titulo(title):
    new_title=""
    title=str(title)
    i=0
    while i < len(title):
        if (title[i] == ',' and title[i-1] == "'" and title[i+2] == "'") or (title[i] == ',' and title[i-1] == '"' and title[i+2] == "'"):
            i=i+1
            while i < len(title):
                if title[i] == "'" or title[i] == "]" or title[i] == "[":
                    pass
                else:
                    new_title=new_title+title[i]
                i=i+1
            i=1+len(title)
        i=i+1

    if new_title == "":
        return title
    else:
        return new_title


def estripar_titulo2(title):
    new_title = ""
    title = str(title)
    i=0
    while i < len(title):
        if title[i] == "'" or title[i] == "]" or title[i] == "[":
            pass
        else:
            new_title = new_title + title[i]
        i = i + 1
    return new_title





from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


def listar_articulos_por_anno(request, year, proveedor_id):
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    anio_obj = Anio.objects.get(anio=year)

    volumenes = Volumen.objects.filter(anio=anio_obj, article__header__proveedor=proveedor).distinct()
    lista_objetos = []

    for volumen in sorted(volumenes, key=alphanumeric_key):
        numeros = sorted(Numero.objects.filter(volumen=volumen, article__header__proveedor=proveedor).distinct(), key=alphanumeric_key)
        numeros_objetos = []

        for numero in numeros:
            articles = Article.objects.filter(header__proveedor=proveedor, anio__anio=year, volumen=volumen, numero=numero)
            numeros_objetos.append({'numero': numero, 'articulos': articles})

        lista_objetos.append({'volumen': volumen, 'numeros': numeros_objetos})

    paginator = Paginator(lista_objetos, 1)  # Número de objetos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    cant=articles.count()

    context = {
        'proveedor': proveedor,
        'page_obj': page_obj,
        'cant': cant,
        'year': year
    }

    return render(request, 'listar_articulos.html', context)




@role_required(['Especialista'])
def cosechar_articulos_de_un_proveedor(request, proveedor_id):
    sets = Set.objects.filter(proveedor_id=proveedor_id)
    context=None

    if request.method == 'POST':
        form = CosecharForm(request.POST)
        if form.is_valid():
            desde_day = form.cleaned_data['desde_dia']
            desde_mes = form.cleaned_data['desde_mes']
            desde_año = form.cleaned_data['desde_año']
            hasta_day = form.cleaned_data['hasta_dia']
            hasta_mes = form.cleaned_data['hasta_mes']
            hasta_año = form.cleaned_data['hasta_año']

        set_value = request.POST.get('set')

        if set_value == "a":
            pass
        else:
            set = get_object_or_404(Set, id=set_value)
            set_value = set.set_spec

        print(set_value)
        i = 0
        if desde_año and desde_mes and desde_day and hasta_day and hasta_mes and hasta_año:
            hasta = date(int(hasta_año), int(hasta_mes), int(hasta_day))
            desde = date(int(desde_año), int(desde_mes), int(desde_day))
            if (desde) and (hasta) and (set_value != "a"):
                context = cosechar_articulo_set_fechas(request, set_value, desde, hasta, proveedor_id)
                i = i + 1
            if (desde) and (hasta) and (set_value == "a"):
                context = cosechar_articulos_fechas(request, desde, hasta, proveedor_id)
                i = i + 1

        if (i == 0) and (set_value != "a"):
            context = cosechar_articulos_set(request, set_value, proveedor_id)

    else:
            form = CosecharForm()


    if context is not None:
        context2 = {
            "context": context,
            "proveedor_id": proveedor_id
        }
        return render(request, 'cosechar_metadatos/cosecha_exitosa.html',context2)
    else:
        context = {
            'form': form,
            'id': proveedor_id,
            'sets': sets,
        }
        return render(request, 'cosechar_metadatos/cosechar_metadatos.html', context)

@role_required(['Especialista'])
def cosechar_articulos_fechas(request,desde,hasta,proveedor_id):
    from_date = datetime.combine(desde, time())  # Convertir desde a datetime.datetime
    to_date = datetime.combine(hasta, time())  # Convertir hasta a datetime.datetime

    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    URL = proveedor.base_url
    registry = MetadataRegistry()
    registry.registerReader('oai_dc', oai_dc_reader)
    client = Client(URL, registry)

    try:
        identifiers= []
        articulos_cosechados = 0
        articulos_ya_existentes = 0
        articulos_sin_metadatos = 0
        total_registros = 0
        for record in client.listRecords(metadataPrefix='oai_dc', from_=from_date, until=to_date):
            header, metadata, _ = record
            try:
                if metadata is not None:
                    # Obtener los campos del encabezado
                    identifier = header.identifier()
                    datestamp = header.datestamp()
                    set_spec = header.setSpec()

                    if Header.objects.filter(identifier=identifier, proveedor_id=proveedor.pk).exists():
                        articulos_ya_existentes = articulos_ya_existentes + 1
                        # articulo_existente = get_object_or_404(Header,identifier=identifier, proveedor_id=proveedor.pk)
                        # identifiers.append(articulo_existente.pk)


                    else:

                        # Crear un objeto de encabezado y guardarlo en la base de datos
                        header_obj = Header.objects.create(
                            identifier=identifier,
                            datestamp=datestamp,
                            set_spec=set_spec,
                            proveedor_id=proveedor.pk
                        )
                        header_obj.save()


                        # Verificar si el idioma existe en el modelo Idioma

                        title = metadata.getField('title')
                        description = metadata.getField('description')
                        subject = metadata.getField('subject')
                        publisher = metadata.getField('publisher')
                        date = metadata.getField('date')
                        identifier_url = metadata.getField('identifier')
                        source = metadata.getField('source')  # Puede haber múltiples fuentes
                        language = metadata.getField('language')
                        rights = metadata.getField('rights')
                        creators_data = metadata.getField('creator')
                        resource_types_data = metadata.getField('type')
                        format = metadata.getField('format')
                        relation = metadata.getField('relation')


                        idioma, created = Idioma.objects.get_or_create(valor=language)

                        volumen, number, year= extract_volume_number_year(str(source[0]),date)

                        anio_obj, created = Anio.objects.get_or_create(anio=year)
                        volumen_obj, created = Volumen.objects.get_or_create(volumen=volumen, anio=anio_obj)
                        numero_obj, created = Numero.objects.get_or_create(numero=number, volumen=volumen_obj)

                        try:
                            title = estripar_titulo(title)
                        except:
                            pass

                        try:
                            title = estripar_titulo2(title)
                        except:
                            pass

                        article = Article.objects.create(
                            header=header_obj,
                            title=title,
                            description=description,
                            publisher=publisher,
                            date=date,
                            identifier_url=identifier_url,
                            source=source,
                            language=idioma,
                            rights=rights,
                            creator=creators_data,
                            resource_types=resource_types_data,
                            format=format,
                            relation=relation,
                            volumen=volumen_obj,
                            numero=numero_obj,
                            anio=anio_obj,
                            subject=subject
                        )

                        article.save()
                        articulos_cosechados = articulos_cosechados + 1


                else:
                    articulos_sin_metadatos = articulos_sin_metadatos +1

            except XMLSyntaxError as xml_error:
                messages.error(request,
                               "Error de sintaxis XML. " + "Detalles: " + str(xml_error))

            total_registros = total_registros + 1
            print(total_registros)

        lista_identificadores = [str(objeto) for objeto in identifiers]
        cadena_identificadores = ','.join(lista_identificadores)


        print("fin del for el que tiene que ser")
        context = {
            "total_registros": total_registros,
            "articulos_cosechados": articulos_cosechados,
            "articulos_ya_existentes": articulos_ya_existentes,
            "articulos_sin_metadatos": articulos_sin_metadatos,
            "identifiers":cadena_identificadores
        }
        return context



    except urllib.error.URLError as e:
        messages.error(request, "No se ha podido establecer conexion con el repositorio. "+"Detalles: "+ str(e))
    except BadArgumentError as e:
        messages.error(request, "Error de argumentos incorrectos. "+"Detalles: "+str(e))
    except BadResumptionTokenError as e:
        messages.error(request, "Error de resumptionToken inválido o expirado. "+"Detalles: "+str(e))
    except CannotDisseminateFormatError as e:
        messages.error(request, "Error de formato de metadatos no compatible. "+"Detalles: "+str(e))
    except NoRecordsMatchError as e:
        messages.error(request, "No hay registros que coincidan. "+"Detalles: "+str(e))
    except NoSetHierarchyError as e:
        messages.error(request, "Jerarquía de conjuntos no admitida. "+"Detalles: "+str(e))
    except Exception as e:
        messages.error(request, "Error Desconocido. "+"Detalles: "+str(e))





@role_required(['Especialista'])
@transaction.atomic
def cosechar_articulo_set_fechas(request,set_value,desde,hasta,proveedor_id):
    from_date = datetime.combine(desde, time())  # Convertir desde a datetime.datetime
    to_date = datetime.combine(hasta, time())  # Convertir hasta a datetime.datetime
    set_spec = set_value



    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    URL = proveedor.base_url
    registry = MetadataRegistry()
    registry.registerReader('oai_dc', oai_dc_reader)
    client = Client(URL, registry)

    try:
        i = 0
        articulos_cosechados = 0
        articulos_ya_existentes = 0
        articulos_sin_metadatos = 0
        total_registros = 0
        for record in client.listRecords(metadataPrefix='oai_dc', from_=from_date, until=to_date, set=set_spec):
            header, metadata, _ = record
            try:
                if metadata is not None:
                    i = i + 1
                    # Obtener los campos del encabezado
                    identifier = header.identifier()
                    datestamp = header.datestamp()
                    set_spec = header.setSpec()

                    if Header.objects.filter(identifier=identifier, proveedor_id=proveedor.pk).exists():
                        articulos_ya_existentes = articulos_ya_existentes + 1

                    else:

                        # Crear un objeto de encabezado y guardarlo en la base de datos
                        header_obj = Header.objects.create(
                            identifier=identifier,
                            datestamp=datestamp,
                            set_spec=set_spec,
                            proveedor_id=proveedor.pk
                        )
                        header_obj.save()
                        print(i)

                        # Verificar si el idioma existe en el modelo Idioma

                        title = metadata.getField('title')
                        description = metadata.getField('description')
                        subject = metadata.getField('subject')
                        publisher = metadata.getField('publisher')
                        date = metadata.getField('date')
                        identifier_url = metadata.getField('identifier')
                        source = metadata.getField('source')  # Puede haber múltiples fuentes
                        language = metadata.getField('language')
                        rights = metadata.getField('rights')
                        creators_data = metadata.getField('creator')
                        resource_types_data = metadata.getField('type')
                        format = metadata.getField('format')
                        relation = metadata.getField('relation')


                        idioma, created = Idioma.objects.get_or_create(valor=language)



                        volumen, number, year= extract_volume_number_year(str(source[0]),date)

                        anio_obj, created = Anio.objects.get_or_create(anio=year)
                        volumen_obj, created = Volumen.objects.get_or_create(volumen=volumen, anio=anio_obj)
                        numero_obj, created = Numero.objects.get_or_create(numero=number, volumen=volumen_obj)


                        try:
                            title=estripar_titulo(title)
                        except:
                            pass

                        try:
                            title = estripar_titulo2(title)
                        except:
                            pass

                        article = Article.objects.create(
                            header=header_obj,
                            title=title,
                            description=description,
                            publisher=publisher,
                            date=date,
                            identifier_url=identifier_url,
                            source=source,
                            language=idioma,
                            rights=rights,
                            creator=creators_data,
                            resource_types=resource_types_data,
                            format=format,
                            relation=relation,
                            volumen=volumen_obj,
                            numero=numero_obj,
                            anio=anio_obj,
                            subject=subject
                        )

                        article.save()
                        articulos_cosechados = articulos_cosechados + 1

                else:
                    articulos_sin_metadatos = articulos_sin_metadatos + 1

            except XMLSyntaxError as xml_error:
                messages.error(request, "Error de sintaxis XML:" + "Detalles: " + str(xml_error))

            total_registros = total_registros + 1
            print(total_registros)

        context = {
            "total_registros": total_registros,
            "articulos_cosechados": articulos_cosechados,
            "articulos_ya_existentes": articulos_ya_existentes,
            "articulos_sin_metadatos": articulos_sin_metadatos
        }
        return context

    except urllib.error.URLError as e:
        messages.error(request, "No se ha podido establecer conexion con el repositorio. " + "Detalles: " + str(e))
    except BadArgumentError as e:
        messages.error(request, "Error de argumentos incorrectos. " + "Detalles: " + str(e))
    except BadResumptionTokenError as e:
        messages.error(request, "Error de resumptionToken inválido o expirado. " + "Detalles: " + str(e))
    except CannotDisseminateFormatError as e:
        messages.error(request, "Error de formato de metadatos no compatible. " + "Detalles: " + str(e))
    except NoRecordsMatchError as e:
        messages.error(request, "No hay registros que coincidan. " + "Detalles: " + str(e))
    except NoSetHierarchyError as e:
        messages.error(request, "NoSetHierarchyError. " + "Detalles: " + str(e))
    except Exception as e:
        messages.error(request, "Jerarquía de conjuntos no admitida. " + "Detalles: " + str(e))


def listar_articulos_por_vol(request,vol_id,proveedor_id):
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    volumen = get_object_or_404(Volumen, id=vol_id)

    numeros = sorted(Numero.objects.filter(volumen=volumen, article__header__proveedor=proveedor).distinct(),
                     key=alphanumeric_key)
    numeros_objetos = []

    for numero in numeros:
        articles = Article.objects.filter(header__proveedor=proveedor, anio__anio=volumen.anio.anio, volumen=volumen,
                                              numero=numero)
        numeros_objetos.append({'numero': numero, 'articulos': articles})

    paginator = Paginator(numeros_objetos, 1)  # Número de objetos por página
    page_number = request.GET.get('page')
    page_vol = paginator.get_page(page_number)

    # for objeto in page_vol:
    #     numero = objeto['numero']
        # articulos = objeto['articulos']

        # Acceder a los atributos del número
        # numero_numero = numero.numero
        # numero_volumen = numero.volumen
        # numero_anio = numero.volumen.anio.anio
        # for articulo in articulos:
        #     titulo = articulo.title


    cant=articles.count()



    context = {
        'proveedor': proveedor,
        'page_vol': page_vol,
        'year': volumen.anio.anio,
        'cant': cant,
        'vol': volumen.volumen
    }

    return render(request, 'listar_articulos.html', context)

def listar_articulos_por_num(request, num_id, proveedor_id):
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    num = get_object_or_404(Numero, id=num_id)
    numeros_objetos = []

    articles = Article.objects.filter(header__proveedor=proveedor, anio__anio=num.volumen.anio.anio, volumen=num.volumen,
                                     numero=num)

    cant=articles.count()
    # Paginar los artículos
    page = request.GET.get('page', 1)
    paginator = Paginator(articles, 10)  # Mostrar 10 artículos por página
    try:
        page_vol = paginator.page(page)
    except PageNotAnInteger:
        page_vol = paginator.page(1)
    except EmptyPage:
        page_vol = paginator.page(paginator.num_pages)

    numeros_objetos.append({'numero': num, 'articulos': page_vol})

    context = {
        'proveedor': proveedor,
        'numeros_objetos': numeros_objetos,
        'year': num.volumen.anio.anio,
        'vol': num.volumen,
        'page': page_vol,
        'cant': cant

    }

    return render(request, 'listar_articulos.html', context)

from django.contrib import messages
import urllib.error

@role_required(['Especialista'])
def cosechar_articulos_set(request,set_value,proveedor_id):
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    URL = proveedor.base_url
    registry = MetadataRegistry()
    registry.registerReader('oai_dc', oai_dc_reader)
    client = Client(URL, registry)


    try:
        articulos_cosechados = 0
        articulos_ya_existentes = 0
        articulos_sin_metadatos = 0
        total_registros = 0
        for record in client.listRecords(metadataPrefix='oai_dc',set=set_value):
            header, metadata, _ = record
            try:
                if metadata is not None:

                    # Obtener los campos del encabezado
                    identifier = header.identifier()
                    datestamp = header.datestamp()
                    set_spec = header.setSpec()

                    if Header.objects.filter(identifier=identifier, proveedor_id=proveedor.pk).exists():
                        articulos_ya_existentes = articulos_ya_existentes + 1

                    else:

                        # Crear un objeto de encabezado y guardarlo en la base de datos
                        header_obj = Header.objects.create(
                            identifier=identifier,
                            datestamp=datestamp,
                            set_spec=set_spec,
                            proveedor_id=proveedor.pk
                        )
                        header_obj.save()


                        # Verificar si el idioma existe en el modelo Idioma

                        title = metadata.getField('title')
                        description = metadata.getField('description')
                        subject = metadata.getField('subject')
                        publisher = metadata.getField('publisher')
                        date = metadata.getField('date')
                        identifier_url = metadata.getField('identifier')
                        source = metadata.getField('source')  # Puede haber múltiples fuentes
                        language = metadata.getField('language')
                        rights = metadata.getField('rights')
                        creators_data = metadata.getField('creator')
                        resource_types_data = metadata.getField('type')
                        format = metadata.getField('format')
                        relation = metadata.getField('relation')

                        idioma, created = Idioma.objects.get_or_create(valor=language)



                        volumen, number, year= extract_volume_number_year(str(source[0]),date)

                        anio_obj, created = Anio.objects.get_or_create(anio=year)
                        volumen_obj, created = Volumen.objects.get_or_create(volumen=volumen, anio=anio_obj)
                        numero_obj, created = Numero.objects.get_or_create(numero=number, volumen=volumen_obj)

                        try:
                            title = estripar_titulo(title)
                        except:
                            pass

                        try:
                            title = estripar_titulo2(title)
                        except:
                            pass

                        article = Article.objects.create(
                            header=header_obj,
                            title=title,
                            description=description,
                            publisher=publisher,
                            date=date,
                            identifier_url=identifier_url,
                            source=source,
                            language=idioma,
                            rights=rights,
                            creator=creators_data,
                            resource_types=resource_types_data,
                            format=format,
                            relation=relation,
                            volumen=volumen_obj,
                            numero=numero_obj,
                            anio=anio_obj,
                            subject=subject
                        )

                        article.save()
                        articulos_cosechados = articulos_cosechados + 1
                else:
                    print("Los metadatos son nulos para este registro.")


            except XMLSyntaxError as xml_error:
                messages.error(request, "Error de sintaxis XML:" + "Detalles: " + str(xml_error))

            total_registros = total_registros + 1
            print(total_registros)

        context = {
            "total_registros": total_registros,
            "articulos_cosechados": articulos_cosechados,
            "articulos_ya_existentes": articulos_ya_existentes,
            "articulos_sin_metadatos": articulos_sin_metadatos
        }
        return context


    except urllib.error.URLError as e:
        messages.error(request, "No se ha podido establecer conexion con el repositorio. " + "Detalles: " + str(e))
    except BadArgumentError as e:
        messages.error(request, "Error de argumentos incorrectos. " + "Detalles: " + str(e))
    except BadResumptionTokenError as e:
        messages.error(request, "Error de resumptionToken inválido o expirado. " + "Detalles: " + str(e))
    except CannotDisseminateFormatError as e:
        messages.error(request, "Error de formato de metadatos no compatible. " + "Detalles: " + str(e))
    except NoRecordsMatchError as e:
        messages.error(request, "No hay registros que coincidan. " + "Detalles: " + str(e))
    except NoSetHierarchyError as e:
        messages.error(request, "NoSetHierarchyError. " + "Detalles: " + str(e))
    except Exception as e:
        messages.error(request, "Jerarquía de conjuntos no admitida. " + "Detalles: " + str(e))


@role_required(['Especialista'])
def modificar_articulo(request, articulo_id):
    article = get_object_or_404(Article, id=articulo_id)

    if request.method == 'POST':
        form = ModificarArticuloForm(request.POST)

        if form.is_valid():
            nuevo_titulo = form.cleaned_data['nuevo_titulo']
            nueva_descripcion = form.cleaned_data['nueva_descripcion']

            article.title = nuevo_titulo
            article.description = nueva_descripcion
            article.save()
            return redirect('ver_articulo', articulo_id=article.id)

    else:
        form = ModificarArticuloForm()

    context = {'article': article, 'form': form}
    return render(request, 'articulo/modificar_articulo.html', context)

@never_cache
def index(request):
    usuarios = User.objects.all().count()
    articulos = Article.objects.all().count()
    revistas = Revista.objects.all().count()

    # Inicializar el objeto page_obj y cantidad
    page_obj = None
    page_range = None
    cantidad = 0

    if request.method == 'GET':
        nombre = request.GET.get('article')

        if nombre is not None:
            # Filtrar artículos por nombre
            articles = Article.objects.filter(title__icontains=nombre)

            # Configurar la paginación
            page = request.GET.get('page', 1)
            paginator = Paginator(articles, 10)  # Mostrar 10 artículos por página

            try:
                page_obj = paginator.page(page)
            except PageNotAnInteger:
                page_obj = paginator.page(1)
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)

            cantidad = articles.count()
            page_range = list(range(max(1, page_obj.number - 2), min(paginator.num_pages, page_obj.number + 3)))


    context = {
        'usuarios': usuarios,
        'articulos': articulos,
        'revistas': revistas,
        'page_obj': page_obj,
        'cantidad': cantidad,
        'nombre': nombre,
        'page_range': page_range,
    }

    return render(request, 'index.html', context)


import re


def extract_volume_number_year(text,date):
    # Patrones de expresiones regulares para encontrar el volumen, número y año
    volume_pattern = r'Vol\.\s*(\d+)'
    number_pattern = r'No\.\s*(\d+)'
    year_pattern = r'\((\d{4})\)|(\d{4})'



    # Buscar y extraer los valores
    volumen = re.search(volume_pattern, text)
    number = re.search(number_pattern, text)
    year = re.search(year_pattern, text)

    volumen = volumen.group(1) if volumen else "1"
    number = number.group(1) if number else "1"
    year = year.group(1) if year.group(1) else year.group(2) if year else "1"

    if number == "1":
        number_pattern = r'Núm\.\s*(\d+)'
        number = re.search(number_pattern, text)
        number = number.group(1) if number else "1"


    # Devolver los valores extraídos
    return volumen, number, year



#
# def ejemplo(request):
#     # Ejemplos de uso
#     print(extract_volume_number_year('Vol. 27 - No. 7 (Julio 1984)'))
#     # Output: {'volume': 27, 'number': 7, 'year': 1984}
#
#     print(extract_volume_number_year(
#         'Journal of Behavior, Health & Social Issues; Vol. 1 No. 2 (2009): Nov-2009 Apr-2010; 21-33'))
#     # Output: {'volume': 1, 'number': 2, 'year': 2009}
#
#     print(extract_volume_number_year('CuidArte Journal; Vol. 10, No.19 (2021): FEBRERO'))
#     # Output: {'volume': 10, 'number': 19, 'year': 2021}
#
#     print(extract_volume_number_year("Ciencias; Núm. 081 (2006)"))
#
#     print(extract_volume_number_year("Amicus Curiae.Segunda Época; Núm. 1(2): Amicus Curiae(2009)"))



def guardar_producto(request):
        return render(request, 'guardar_producto.html')




#
# def guardar_producto2(request):
#     if request.method == 'POST':
#         nombre = request.POST.get('nombre')
#         producto = Producto(nombre=nombre)
#         producto.save()
#         return JsonResponse({'success': True})
#     else:
#         return JsonResponse({'success': False, 'error': 'Método no permitido'})




import json
# def actualizar_articulos(request,identifiers):
#     articulos_actualizados=0
#     articulos_sin_actualizar=0
#     articulos_a_actualizar=0
#     if request.method == 'POST':
#         list_identifiers=identifiers.split(',')
#         try:
#             for id in list_identifiers:
#                 bandera=cosechar_metadatos_de_un_articulo(id)
#                 if bandera is True:
#                     articulos_actualizados=articulos_actualizados+1
#                 else:
#                     articulos_sin_actualizar=articulos_sin_actualizar+1
#                 articulos_a_actualizar = articulos_a_actualizar+1
#
#         except urllib.error.URLError as e:
#             messages.error(request, "No se ha podido establecer conexion con el repositorio. " + "Detalles: " + str(e))
#         except BadArgumentError as e:
#             messages.error(request, "Error de argumentos incorrectos. " + "Detalles: " + str(e))
#         except BadResumptionTokenError as e:
#             messages.error(request, "Error de resumptionToken inválido o expirado. " + "Detalles: " + str(e))
#         except CannotDisseminateFormatError as e:
#             messages.error(request, "Error de formato de metadatos no compatible. " + "Detalles: " + str(e))
#         except NoRecordsMatchError as e:
#             messages.error(request, "No hay registros que coincidan. " + "Detalles: " + str(e))
#         except NoSetHierarchyError as e:
#             messages.error(request, "NoSetHierarchyError. " + "Detalles: " + str(e))
#         except Exception as e:
#             messages.error(request, "Jerarquía de conjuntos no admitida. " + "Detalles: " + str(e))
#
#     context = {
#         "articulos_actualizados":articulos_actualizados,
#         "articulos_sin_actualizar":articulos_sin_actualizar,
#         "articulos_a_actualizar":articulos_a_actualizar
#
#     }
#     return render(request,'cosechar_metadatos/actualizar_registros_exitoso.html',context)






def cosechar_metadatos_de_un_articulo(id):
    header2=get_object_or_404(Header,id=id)
    base_url2 = header2.proveedor.base_url
    identifier2 = header2.identifier
    registry = MetadataRegistry()
    registry.registerReader('oai_dc', oai_dc_reader)
    client = Client(base_url2, registry)

    try:
        record = client.getRecord(identifier=identifier2, metadataPrefix='oai_dc')
        header, metadata, _ = record

        if metadata is not None:
            identifier = header.identifier()
            datestamp = header.datestamp()
            set_spec = header.setSpec()

            # Crear un objeto de encabezado y guardarlo en la base de datos
            header_obj = Header.objects.create(
                identifier=identifier,
                datestamp=datestamp,
                set_spec=set_spec,
                proveedor_id=header2.proveedor.pk
            )
            header_obj.save()

            # Verificar si el idioma existe en el modelo Idioma

            title = metadata.getField('title')
            description = metadata.getField('description')
            subject = metadata.getField('subject')
            publisher = metadata.getField('publisher')
            date = metadata.getField('date')
            identifier_url = metadata.getField('identifier')
            source = metadata.getField('source')  # Puede haber múltiples fuentes
            language = metadata.getField('language')
            rights = metadata.getField('rights')
            creators_data = metadata.getField('creator')
            resource_types_data = metadata.getField('type')
            format = metadata.getField('format')
            relation = metadata.getField('relation')

            idioma, created = Idioma.objects.get_or_create(valor=language)

            volumen, number, year = extract_volume_number_year(str(source[0]), date)

            anio_obj, created = Anio.objects.get_or_create(anio=year)
            volumen_obj, created = Volumen.objects.get_or_create(volumen=volumen, anio=anio_obj)
            numero_obj, created = Numero.objects.get_or_create(numero=number, volumen=volumen_obj)

            try:
                title = estripar_titulo(title)
            except:
                pass

            try:
                title = estripar_titulo2(title)
            except:
                pass

            article = Article.objects.create(
                header=header_obj,
                title=title,
                description=description,
                publisher=publisher,
                date=date,
                identifier_url=identifier_url,
                source=source,
                language=idioma,
                rights=rights,
                creator=creators_data,
                resource_types=resource_types_data,
                format=format,
                relation=relation,
                volumen=volumen_obj,
                numero=numero_obj,
                anio=anio_obj,
                subject=subject
            )

            article.save()
            return True
    except:
        return False


def actualizar_vol(request,id_vol):
    vol=get_object_or_404(Volumen,id=id_vol)
    articles = Article.objects.filter(volumen=vol)
    articulos_actualizados=0
    articulos_sin_actualizar=0
    articulos_a_actualizar=0
    try:
        for article in articles:
            bandera = cosechar_metadatos_de_un_articulo(article.header.id)
            if bandera is True:
                articulos_actualizados = articulos_actualizados + 1
                article.header.delete()
                article.delete()
            else:
                articulos_sin_actualizar = articulos_sin_actualizar + 1
            articulos_a_actualizar = articulos_a_actualizar + 1
            print(articulos_a_actualizar)
    except urllib.error.URLError as e:
        messages.error(request, "No se ha podido establecer conexion con el repositorio. " + "Detalles: " + str(e))
    except BadArgumentError as e:
        messages.error(request, "Error de argumentos incorrectos. " + "Detalles: " + str(e))
    except BadResumptionTokenError as e:
        messages.error(request, "Error de resumptionToken inválido o expirado. " + "Detalles: " + str(e))
    except CannotDisseminateFormatError as e:
        messages.error(request, "Error de formato de metadatos no compatible. " + "Detalles: " + str(e))
    except NoRecordsMatchError as e:
        messages.error(request, "No hay registros que coincidan. " + "Detalles: " + str(e))
    except NoSetHierarchyError as e:
        messages.error(request, "NoSetHierarchyError. " + "Detalles: " + str(e))
    except Exception as e:
        messages.error(request, "Jerarquía de conjuntos no admitida. " + "Detalles: " + str(e))

    context = {
        "articulos_actualizados":articulos_actualizados,
        "articulos_sin_actualizar":articulos_sin_actualizar,
        "articulos_a_actualizar":articulos_a_actualizar

    }
    return render(request,'cosechar_metadatos/actualizar_registros_exitoso.html',context)

def listar_articulos_por_autor(request, creator=None):
    # Obtener la página actual de la URL

    if creator is None:
        creator = request.GET.get('creator', '')

    page_number = request.GET.get('page', 1)
    # Filtrar los artículos por el nombre del autor (utilizando icontains en lugar de contains)

    articles = Article.objects.filter(creator__icontains=creator)


    # Crear el paginador y obtener la página actual
    paginator = Paginator(articles, 10)  # Mostrar 10 artículos por página
    page_obj = paginator.get_page(page_number)

    # Obtener la cantidad total de artículos
    cantidad = articles.count()

    context = {
        'articles': page_obj,
        'creator': creator,
        'cantidad': cantidad,
    }
    return render(request, 'articulo/article_list_autor.html', context)


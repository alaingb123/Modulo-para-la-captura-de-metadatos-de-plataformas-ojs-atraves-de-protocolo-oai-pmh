from django.core.paginator import Paginator
from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, oai_dc_reader

from harvest.forms import ProveedorForm,RevistaForm

from oaipmh.error import NoMetadataFormatsError
from django.shortcuts import redirect
from harvest.models import Proveedor, Set, MetadataFormat, Revista, Article, Numero, Volumen, Clasificacion, \
    Subclasificacion
from django.contrib import messages
from django.shortcuts import render, get_object_or_404

from usuario.decorator import role_required
from .models import Anio


from django.urls import reverse


@role_required(['Especialista'])
def registrar_proveedor(request):
    metadata_registry = MetadataRegistry()
    metadata_registry.registerReader('oai_dc', oai_dc_reader)
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            # Procesar los datos del formulario
            base_url = form.cleaned_data['base_url']
            client = Client(base_url, metadata_registry)

            try:
                identify_response = client.identify()
                repository_name = identify_response.repositoryName()
                base_url = identify_response.baseURL()
                protocol_version = identify_response.protocolVersion()
                earliest_datestamp = identify_response.earliestDatestamp()
                deleted_record_policy = identify_response.deletedRecord()
                granularity = identify_response.granularity()

                proveedor = Proveedor(
                    repository_name=repository_name,
                    base_url=base_url,
                    protocol_version=protocol_version,
                    earliest_datestamp=earliest_datestamp,
                    deleted_record_policy=deleted_record_policy,
                    granularity=granularity
                )
                proveedor.save()

                sets = client.listSets()
                for s in sets:
                    set_spec = s[0]  # Código del conjunto
                    set_name = s[1]  # Nombre del conjunto

                    conjunto = Set(
                        proveedor=proveedor,
                        set_spec=set_spec,
                        set_name=set_name
                    )
                    conjunto.save()

                metadata_formats = client.listMetadataFormats()
                for metadata_format in metadata_formats:
                    metadata_prefix = metadata_format[0]  # Prefijo del formato de metadatos
                    metadata_namespace = metadata_format[1]  # Espacio de nombres del formato de metadatos
                    schema = metadata_format[2]  # Enlace al esquema del formato de metadatos

                    metadata_F = MetadataFormat(
                        prefix=metadata_prefix,
                        schema = schema,
                        proveedor = proveedor,
                        namespace = metadata_namespace
                    )
                    metadata_F.save()



                url = reverse('agregar_datos_revista', args=[proveedor.id])
                return redirect(url)  # Redirecciona a una URL o vista específica para mostrar el mensaje de registro exitoso
            except NoMetadataFormatsError:
                messages.error(request, "Error: No se encontraron formatos de metadatos compatibles con el proveedor.")
            except Exception as e:
                error_message = "Error al realizar la solicitud: " + str(e)
                if "badArgument" in error_message:
                    messages.error(request, "Error: Argumento no válido.")
                elif "badResumptionToken" in error_message:
                    messages.error(request, "Error: El token de reanudación es inválido o ha expirado.")
                elif "badVerb" in error_message:
                    messages.error(request, "Error: Verbo no válido.")
                elif "cannotDisseminateFormat" in error_message:
                    messages.error(request, "Error: Formato de metadatos no compatible.")
                elif "idDoesNotExist" in error_message:
                    messages.error(request, "Error: El identificador no existe.")
                elif "noRecordsMatch" in error_message:
                    messages.error(request, "Error: No se encontraron registros que coincidan.")
                elif "noMetadataFormats" in error_message:
                    messages.error(request, "Error: No hay formatos de metadatos disponibles.")
                elif "noSetHierarchy" in error_message:
                    messages.error(request, "Error: El repositorio no admite conjuntos.")
                else:
                    messages.error(request, error_message)
    else:
        form = ProveedorForm()

    for field in form.fields.values():
        field.widget.attrs.update({
            'class': 'form-control',
            'placeholder': field.label
        })
    return render(request, 'registro_proveedor.html', {'form': form})


def buscar_proveedor_por_id(proveedor_id):
    try:
        proveedor = Proveedor.objects.get(id=proveedor_id)
        return proveedor
    except Proveedor.DoesNotExist:
        return None


def agregar_datos_revista(request, proveedor_id):
    if request.method == 'POST':
        form = RevistaForm(request.POST)
        if form.is_valid():
            proveedor = buscar_proveedor_por_id(proveedor_id)
            editores = form.cleaned_data['editores']
            subclasificacion = form.cleaned_data['subclasificacion']
            autores = form.cleaned_data['autores']
            if proveedor:
                revista = form.save(commit=False)
                revista.proveedor = proveedor


                revista.save()
                revista.editores.set(editores)
                revista.subclasificacion.set(subclasificacion)
                revista.autores.set(autores)
                revista.save()
            else:
                messages.error(request, 'El proveedor no existe.')
            return redirect('listar_clasificaciones')  # Redirecciona a una URL o vista específica para mostrar el mensaje de registro exitoso
    else:
        form = RevistaForm()


    subsclasi=Subclasificacion.objects.all()

    # Agregar clases CSS y placeholders a los campos del formulario
    fields = list(form.fields.values())
    rows = [fields[i:i+2] for i in range(0, len(fields), 2)]
    for row in rows:
        for field in row:
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label,
            })

    return render(request, 'registro_revista.html', {'form': form ,"subsclasi":subsclasi})


def listar_clasificaciones(request):
    clasificaciones = Clasificacion.objects.all()
    subclasificaciones = Subclasificacion.objects.all()
    clasificaciones_con_subclasificaciones = {}

    # Agrupar las subclasificaciones por clasificación
    for clasificacion in clasificaciones:
        subclasificaciones_clasificacion = []
        for subclasificacion in subclasificaciones:
            if subclasificacion.clasificacion == clasificacion:
                subclasificaciones_clasificacion.append(subclasificacion)
        clasificaciones_con_subclasificaciones[clasificacion] = subclasificaciones_clasificacion

    return render(request, 'lista_clasificaciones.html', {
        'clasificaciones': clasificaciones,
        'clasificaciones_con_subclasificaciones': clasificaciones_con_subclasificaciones
    })



import re

def alphanumeric_key(value):
    parts = re.split(r'(\d+)', str(value))
    return [int(part) if part.isdigit() else part for part in parts]
def ver_revista_proveedor(request, proveedor_id):
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    anios = Anio.objects.filter(article__header__proveedor=proveedor).distinct()


    lista_anidada=[[[]]]
    for anio in sorted(anios, key=alphanumeric_key):
        articulos_anio = Article.objects.filter(header__proveedor=proveedor, anio=anio).count()

        anio_data = {
            'anio': anio.anio,
            'articulos': articulos_anio,
            'volumenes': []
        }
        volumenes = Volumen.objects.filter(anio=anio, article__header__proveedor=proveedor).distinct()
        for volumen in sorted(volumenes, key=alphanumeric_key):
            volumen_data = {
                'volumen': volumen,
                'numeros': sorted(Numero.objects.filter(volumen=volumen,article__header__proveedor=proveedor).distinct(), key=alphanumeric_key)
            }
            anio_data['volumenes'].append(volumen_data)

        lista_anidada.append(anio_data)

    subs = proveedor.revista.subclasificacion.all()
    clasificaciones = set()

    for sub in subs:
        clasificaciones.add(sub.clasificacion)

    context = {
        'proveedor': proveedor,
        'lista_anidada': lista_anidada,
        'clasificaciones': clasificaciones,
    }

    return render(request, 'vizualizar_revistas.html', context)




@role_required(['Especialista'])
def eliminar_proveedor(request,proveedor_id):
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    proveedor.delete()
    return redirect('listar_clasificaciones')


def modificar_revista(request, revista_id):
    revista = get_object_or_404(Revista, id=revista_id)

    if request.method == 'POST':
        form = RevistaForm(request.POST, instance=revista)
        if form.is_valid():
            form.save()
            return redirect('ver_revista', proveedor_id=revista.proveedor.id)
        else:
            # Aplicar estilos personalizados a los inputs
            for field in form.fields.values():
                if field.widget.__class__.__name__ == 'SelectMultiple':
                    field.widget.attrs.update({'class': 'js-multiple-select form-control'})
                else:
                    field.widget.attrs.update({'class': 'form-control'})
    else:
        form = RevistaForm(instance=revista)

        # Aplicar estilos personalizados a los inputs
        for field in form.fields.values():
            if field.widget.__class__.__name__ == 'SelectMultiple':
                field.widget.attrs.update({'class': 'js-multiple-select form-control'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

    return render(request, 'modificar_revista.html', {'form': form, 'revista': revista})




def obtener_revista(revista_id):
    revista=get_object_or_404(Revista, id=revista_id)
    return revista

def listar_revistas(request,subclasificacion_id):
    subclasificacion = Subclasificacion.objects.get(id=subclasificacion_id)
    revistas = Revista.objects.filter(subclasificacion=subclasificacion)

    paginator = Paginator(revistas, 10)  # Divide las revistas en páginas, mostrando 10 revistas por página
    page_number = request.GET.get('page')  # Obtiene el número de página actual desde los parámetros GET
    page_obj = paginator.get_page(page_number)  # Obtiene el objeto de página actual

    context = {
        'subclasificacion': subclasificacion,
        'page_obj': page_obj
    }
    return render(request, 'lista_revistas.html', context)

def buscar_revistas(request):
    if request.method == 'GET':
        nombre = request.GET.get('nombre')
        clasificaciones_seleccionadas = request.GET.getlist('clasificacion')

        clasificaciones = Clasificacion.objects.all()

        ids_clasificaciones_seleccionadas = [clasificacion.id for clasificacion in clasificaciones if
                                             clasificacion.valor in clasificaciones_seleccionadas]

        revistas = Revista.objects.all()

        if 'limpiar' in request.GET:
            nombre = None
            clasificaciones_seleccionadas = None


        if nombre:
            revistas = revistas.filter(proveedor__repository_name__icontains=nombre)

        if clasificaciones_seleccionadas:
            revistas = revistas.filter(subclasificacion__clasificacion__in=ids_clasificaciones_seleccionadas)

        page_number = request.GET.get('page')
        paginator = Paginator(revistas, 10)
        page_obj = paginator.get_page(page_number)



        context = {
            'nombre': nombre,
            'revistas': page_obj,
            'clasificaciones': clasificaciones,
            'clasificaciones_seleccionadas': clasificaciones_seleccionadas,
        }

        return render(request, 'Revista_proveedor/buscar_revista.html', context)

    clasificaciones = Clasificacion.objects.all()  # Obtener todas las clasificaciones

    context = {
        'clasificaciones': clasificaciones,
    }

    return render(request, 'Revista_proveedor/buscar_revista.html', context)
from django.db.models import Count
def listar_proveedores(request):
    proveedores_sin_revista=[]
    proveedores = Proveedor.objects.all()
    for proveedor in proveedores:
        try:
            proveedor.revista
        except:
            proveedores_sin_revista.append(proveedor)
    context = {
        'proveedores_sin_revista': proveedores_sin_revista,
    }

    return render(request, 'Revista_proveedor/listar_proveedores_sin_revista.html', context)

def acercade (request):
    return render(request,'Acerca de.html')



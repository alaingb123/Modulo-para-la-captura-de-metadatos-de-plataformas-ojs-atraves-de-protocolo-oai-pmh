from django.shortcuts import render
# Create your views here.
from django.http import HttpResponse,JsonResponse
from datetime import datetime

from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, oai_dc_reader
from oaipmh.error import IdDoesNotExistError
from oaipmh.error import NoMetadataFormatsError


def datetime_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
def cosechar_metadatos_prueba(request):
    URL = 'https://publicaciones.uci.cu/index.php/serie/oai'
    registry = MetadataRegistry()
    registry.registerReader('oai_dc', oai_dc_reader)
    client = Client(URL, registry)

    for record in client.listRecords(metadataPrefix='oai_dc'):
        header, metadata, _ = record
        if metadata is not None:
            print(metadata.getField('title'))
            print(metadata.getField('creator'))
            print(metadata.getField('date'))
            for field, value in metadata.getMap().items():
                print(field, value)
        else:
            print("Los metadatos son nulos para este registro.")

from oaipmh.error import XMLSyntaxError

def cosechar_metadatos_de_un_articulo(request):
    base_url = 'https://publicaciones.uci.cu/index.php/serie/oai'  # URL base del servidor OAI-PMH
    identifier = 'oai:https://publicaciones.uci.cu/oai:article/83'  # Identificador único del artículo
    base_url2 = 'https://revistas.ucr.ac.cr/index.php/index/oai'
    identifier2 = 'oai:portal.ucr.ac.cr:article/1532'

    registry = MetadataRegistry()
    registry.registerReader('oai_dc', oai_dc_reader)
    client = Client(base_url2, registry)

    try:
        record = client.getRecord(identifier=identifier2, metadataPrefix='oai_dc')
        header, metadata, _ = record
        if metadata is not None:
            # Obtener los metadatos del artículo encontrado
            metadatos = metadata.getMap()
            # Devolver los metadatos como una respuesta HTTP
            title = metadatos.get('title', [])
            creator = metadatos.get('creator', [])
            subject = metadatos.get('subject', [])
            description = metadatos.get('description', [])
            publisher = metadatos.get('publisher', [])
            contributor = metadatos.get('contributor', [])
            date = metadatos.get('date', [])
            type = metadatos.get('type', [])
            format = metadatos.get('format', [])
            identifier = metadatos.get('identifier', [])
            source = metadatos.get('source', [])
            language = metadatos.get('language', [])
            relation = metadatos.get('relation', [])
            coverage = metadatos.get('coverage', [])
            rights = metadatos.get('rights', [])

            header_id = header.identifier()
            header_datestamp = header.datestamp()
            header_set_spec = header.setSpec()

            header_data = {
                'identifier': header_id,
                'datestamp': header_datestamp,
                'set_spec': header_set_spec,
            }

            # Combinar los metadatos y el encabezado en un solo diccionario
            response_data = {
                'header': header_data,
                'metadata': metadatos
            }

            # Devolver los datos combinados como una respuesta HTTP en formato JSON
            import json


            # Devolver los metadatos como una respuesta HTTP
            return JsonResponse(response_data, json_dumps_params={'default': datetime_serializer})
        else:
            print("Los metadatos son nulos para este registro.")
    except XMLSyntaxError as e:
        print("Error de sintaxis XML en la respuesta del servidor OAI-PMH:", e)
        # Si ocurre un error, puedes devolver una respuesta de error
        return HttpResponse("Error de sintaxis XML en la respuesta del servidor OAI-PMH", status=500)
    except IdDoesNotExistError as e:
        print("El artículo no se encontró:", e)
        # Si el artículo no se encuentra, puedes devolver una respuesta de error
        return HttpResponse("El artículo no se encontró", status=404)


def proveedor(request):
    metadata_registry = MetadataRegistry()
    metadata_registry.registerReader('oai_dc', oai_dc_reader)

    base_url = 'https://publicaciones.uci.cu/index.php/serie/oai'
    base_url2 = 'https://revistas.ucr.ac.cr/index.php/index/oai'
    client = Client(base_url2, metadata_registry)

    try:
        # Identify
        identify_response = client.identify()
        repository_name = identify_response.repositoryName()
        base_url = identify_response.baseURL()
        protocol_version = identify_response.protocolVersion()
        earliest_datestamp = identify_response.earliestDatestamp()
        deleted_record_policy = identify_response.deletedRecord()
        granularity = identify_response.granularity()

        # Metadata formats
        metadata_formats = client.listMetadataFormats()
        for metadata_format in metadata_formats:
            metadata_prefix = metadata_format[0]  # Prefijo del formato de metadatos
            metadata_namespace = metadata_format[1]  # Espacio de nombres del formato de metadatos
            schema = metadata_format[2]  # Enlace al esquema del formato de metadatos

            print("Metadata Prefix:", metadata_prefix)
            print("Metadata Namespace:", metadata_namespace)
            print("Schema:", schema)
            print("----------------------")

        # print("Repository Name:", repository_name)
        # print("Base URL:", base_url)
        # print("Protocol Version:", protocol_version)
        # print("Earliest Datestamp:", earliest_datestamp)
        # print("Deleted Record Policy:", deleted_record_policy)
        # print("Granularity:", granularity)

    except NoMetadataFormatsError:
        print("Error: No se encontraron formatos de metadatos compatibles con el proveedor.")
    except Exception as e:
        print("Error al realizar la solicitud:", str(e))

    sets = client.listSets()
    for s in sets:
        set_spec = s[0]  # Código del conjunto
        set_name = s[1]  # Nombre del conjunto

        # print("Set Spec:", set_spec)
        # print("Set Name:", set_name)
        # print("----------------------")



def cosechar_metadatos_de_un_año(request):
    from_date = datetime(2020, 1, 1)
    to_date = datetime(2024, 12, 31)
    set_spec='serie:AO'

    URL = 'https://publicaciones.uci.cu/index.php/serie/oai'
    registry = MetadataRegistry()
    registry.registerReader('oai_marc', oai_dc_reader)
    client = Client(URL, registry)

    # Realizar la solicitud de cosecha con el rango de fechas
    i=0
    for record in client.listRecords(metadataPrefix='oai_marc', from_=from_date, until=to_date, set=set_spec):
        header, metadata, _ = record
        if metadata is not None:
            print(i)
            i=i+1
            print("El setspec es :",header.setSpec())
            print(metadata.getField('title'))
            print(metadata.getField('creator'))
            print(metadata.getField('date'))
            print(metadata.getField('source'))
        else:
            print("Los metadatos son nulos para este registro.")
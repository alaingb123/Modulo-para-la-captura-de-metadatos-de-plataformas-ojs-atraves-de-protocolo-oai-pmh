from django.contrib import admin
from django.urls import path,include
from harvest.viewR import registrar_proveedor, agregar_datos_revista, listar_clasificaciones, ver_revista_proveedor, \
    eliminar_proveedor, modificar_revista, listar_revistas, buscar_revistas,listar_proveedores,acercade
from harvest.views import listar_articulos_por_anno, ver_articulo, \
    cosechar_articulos_de_un_proveedor, estripar_titulo, listar_articulos_por_vol, listar_articulos_por_num, \
    modificar_articulo,actualizar_vol,listar_articulos_por_autor




urlpatterns = [

    #Revista__proveedor
    path('registrar_proveedor/',registrar_proveedor, name= 'registrar_proveedor' ),
    path('agregar_datos_revista/<int:proveedor_id>/', agregar_datos_revista, name='agregar_datos_revista'),
    path('listar_clasificaciones/', listar_clasificaciones, name='listar_clasificaciones'),
    path('listar_revistas/<int:subclasificacion_id>/', listar_revistas, name='listar_revistas'),
    path('buscar_revistas/', buscar_revistas, name='buscar_revistas'),
    path('ver_revista/<int:proveedor_id>/', ver_revista_proveedor, name='ver_revista'),
    path('eliminar_proveedor/<int:proveedor_id>/', eliminar_proveedor, name='eliminar_proveedor'),
    path('modificar_revista/<int:revista_id>/', modificar_revista, name='modificar_revista'),
    path('listar_proveedores/', listar_proveedores, name='listar_proveedores'),

    #Articulos
    path('listar_articulos_por_anno/<str:year>/<int:proveedor_id>/', listar_articulos_por_anno, name='listar_articulos_por_anno'),
    path('listar_articulos_por_volumen/<int:vol_id>/<int:proveedor_id>/', listar_articulos_por_vol, name='listar_articulos_por_vol'),
    path('listar_articulos_por_num/<int:num_id>/<int:proveedor_id>/', listar_articulos_por_num, name='listar_articulos_por_num'),
    path('listar_articulos_por_autor/<str:creator>/', listar_articulos_por_autor, name='listar_articulos_por_autor'),
    path('listar_articulos_por_autor2/', listar_articulos_por_autor, name='listar_articulos_por_autor2'),
    path('articulo/<int:articulo_id>/', ver_articulo, name='ver_articulo'),
    path('modificar_articulo/<int:articulo_id>/', modificar_articulo, name='modificar_articulo'),

        #Cosechar articulos
        path('cosechar_articulos/<int:proveedor_id>/', cosechar_articulos_de_un_proveedor, name='cosechar_articulos'),
        path('titulo/', estripar_titulo, name='titulo'),

    path('actualizar_vol/<int:id_vol>/',actualizar_vol, name='actualizar_vol'),

    path('acercade/',acercade, name='acercade'),





]
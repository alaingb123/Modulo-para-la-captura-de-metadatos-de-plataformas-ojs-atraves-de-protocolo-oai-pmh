


from django.urls import path,include

from usuario.views import crear_usuario, iniciar_sesion, editar_perfil, eliminar_usuario,cerrar_sesion

urlpatterns = [


        path('crear_usuario/', crear_usuario, name='crear_usuario'),
        path('iniciar_sesion/', iniciar_sesion, name='iniciar_sesion'),
        path('editar_perfil/', editar_perfil, name='editar_perfil'),
        path('eliminar_usuario/', eliminar_usuario, name='eliminar_usuario'),
        path('cerrar_sesion/', cerrar_sesion, name='cerrar_sesion'),


]
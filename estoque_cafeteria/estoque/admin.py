from django.contrib import admin
from .models import Loja, Categoria, Produto, MovimentoEstoque, UserLoja
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

class UserAdmin(BaseUserAdmin):
    # Adicionando o campo 'loja' nos formulários de edição
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informações de Loja', {'fields': ('loja',)}),
    )

    # Incluindo o campo 'loja' na listagem de usuários no admin
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'loja')
    list_filter = ('is_staff', 'is_active', 'loja')

# Desregistrar o User padrão e registrar o novo
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# Personalização para o modelo Loja
@admin.register(Loja)
class LojaAdmin(admin.ModelAdmin):
    list_display = ('nome','logo')
    search_fields = ('nome',)



# Personalização para o modelo Categoria
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'loja')
    search_fields = ('nome',)
    list_filter = ('loja',)

# Personalização para o modelo Produto
@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'quantidade', 'tipo_quantidade', 'validade', 'estoque_minimo', 'status', 'loja', 'alterado_por', 'categoria')
    search_fields = ('nome', 'quantidade')
    list_filter = ('tipo_quantidade', 'status', 'loja', 'categoria')
    list_editable = ('quantidade', 'estoque_minimo', 'status')

# Personalização para o modelo MovimentoEstoque
@admin.register(MovimentoEstoque)
class MovimentoEstoqueAdmin(admin.ModelAdmin):
    list_display = ('produto', 'tipo_movimento', 'quantidade', 'data_movimento', 'responsavel', 'loja')
    search_fields = ('produto__nome',)
    list_filter = ('tipo_movimento', 'loja', 'data_movimento')
    date_hierarchy = 'data_movimento'

@admin.register(UserLoja)
class UserLoja(admin.ModelAdmin):
    list_display = ('user', 'loja')
    search_fields = ('user', 'loja')
    list_filter = ('loja',)
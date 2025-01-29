import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.test import RequestFactory
from django.http import HttpResponseNotAllowed
from django.contrib.messages.middleware import MessageMiddleware
from unittest.mock import patch
from app.views import login  # Substitua 'app' pelo nome do seu aplicativo

@pytest.mark.django_db
class TestLoginView:
    def setup_method(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", password="testpassword")

    def add_messages_middleware(self, request):
        """Adiciona suporte a mensagens na requisição simulada."""
        middleware = MessageMiddleware(lambda req: None)
        middleware.process_request(request)
        return request

    def test_login_head_method(self):
        """Testa se o método HEAD retorna status 200."""
        request = self.factory.head(reverse('login'))
        response = login(request)
        assert response.status_code == 200

    def test_login_get_method(self):
        """Testa se o método GET renderiza a página de login corretamente."""
        request = self.factory.get(reverse('login'))
        response = login(request)
        assert response.status_code == 200
        assert 'login.html' in response.template_name

    @patch('app.views.authenticate')
    @patch('app.views.login_django')
    @patch('app.views.tour_site')
    @patch('app.views.func_notifica_vencimento')
    def test_login_post_success(self, mock_notifica, mock_tour, mock_login, mock_auth):
        """Testa login com credenciais válidas."""
        mock_auth.return_value = self.user

        request = self.factory.post(reverse('login'), {'nome': 'testuser', 'senha': 'testpassword'})
        request.user = self.user
        response = login(request)

        mock_auth.assert_called_once_with(username='testuser', password='testpassword')
        mock_login.assert_called_once_with(request, self.user)
        mock_tour.assert_called_once_with(request)
        mock_notifica.assert_called_once_with(request)

        assert response.status_code == 302  # Redirecionamento esperado
        assert response.url == reverse('produtoview')

    @patch('app.views.authenticate')
    def test_login_post_fail(self, mock_auth):
        """Testa login com credenciais inválidas."""
        mock_auth.return_value = None

        request = self.factory.post(reverse('login'), {'nome': 'wronguser', 'senha': 'wrongpass'})
        request = self.add_messages_middleware(request)
        response = login(request)

        mock_auth.assert_called_once_with(username='wronguser', password='wrongpass')

        assert response.status_code == 302  # Redirecionamento esperado
        assert response.url == reverse('login')

    def test_login_invalid_method(self):
        """Testa se métodos HTTP não permitidos retornam HttpResponseNotAllowed."""
        request = self.factory.put(reverse('login'))
        response = login(request)
        assert isinstance(response, HttpResponseNotAllowed)
        assert response.status_code == 405

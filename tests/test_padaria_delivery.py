# tests/test_padaria_delivery.py
import pytest
from unittest.mock import MagicMock, patch
from collections import namedtuple
from app.tenants.padaria.tools import (
    calcular_valor_por_distancia,
    geocodificar_com_fallback,
    calcular_taxa_entrega_handler
)

LocationMock = namedtuple("LocationMock", ["latitude", "longitude"])

class TestTabelaDePrecosEntrega:
    """Testes unitários para a regra de cálculo por distância."""

    def test_distancia_gratis_ate_500_metros(self):
        valor, permitida = calcular_valor_por_distancia(0.3)
        assert permitida is True
        assert valor == 0.0

        valor, permitida = calcular_valor_por_distancia(0.5)
        assert permitida is True
        assert valor == 0.0

    def test_distancia_ate_1_km(self):
        valor, permitida = calcular_valor_por_distancia(0.8)
        assert permitida is True
        assert valor == 7.0

        valor, permitida = calcular_valor_por_distancia(1.0)
        assert permitida is True
        assert valor == 7.0

    def test_distancia_ate_2_km(self):
        valor, permitida = calcular_valor_por_distancia(1.5)
        assert permitida is True
        assert valor == 8.0

        valor, permitida = calcular_valor_por_distancia(2.0)
        assert permitida is True
        assert valor == 8.0

    def test_distancia_ate_3_km(self):
        valor, permitida = calcular_valor_por_distancia(2.8)
        assert permitida is True
        assert valor == 9.0

        valor, permitida = calcular_valor_por_distancia(3.0)
        assert permitida is True
        assert valor == 9.0

    def test_distancia_acima_de_3_km_com_adicional(self):
        # 4.2 km -> 9.0 + ceil(1.2) * 1.0 = 9 + 2 = R$ 11.00
        valor, permitida = calcular_valor_por_distancia(4.2)
        assert permitida is True
        assert valor == 11.0

        # 10.0 km -> 9.0 + ceil(7.0) * 1.0 = 9 + 7 = R$ 16.00
        valor, permitida = calcular_valor_por_distancia(10.0)
        assert permitida is True
        assert valor == 16.0

    def test_distancia_acima_de_10_km_rejeitada(self):
        valor, permitida = calcular_valor_por_distancia(10.1)
        assert permitida is False

        valor, permitida = calcular_valor_por_distancia(325.0)
        assert permitida is False


class TestGeocodificacaoFallback:
    """Testes unitários para a busca com fallback."""

    def test_busca_exata_sucesso(self):
        geolocator_mock = MagicMock()
        geolocator_mock.geocode.return_value = LocationMock(-21.1767, -47.8108)

        resultado = geocodificar_com_fallback(geolocator_mock, "Rua Pedro Giacheto, 184, Ribeirão Preto")
        assert resultado is not None
        assert resultado.latitude == -21.1767

    def test_fallback_remove_numeros_quando_primeira_falha(self):
        geolocator_mock = MagicMock()
        geolocator_mock.geocode.side_effect = [None, LocationMock(-21.1700, -47.8100)]

        resultado = geocodificar_com_fallback(geolocator_mock, "Rua Inexistente, 999, Ribeirão Preto")
        assert resultado is not None
        assert resultado.latitude == -21.1700
        assert geolocator_mock.geocode.call_count == 2


class TestHandlerToolCalculoTaxa:
    """Testes com mocks para o handler executado pelo Gemini."""

    @patch("app.tenants.padaria.tools.Nominatim")
    def test_handler_entrega_dentro_do_limite(self, mock_nominatim_class):
        mock_geolocator = MagicMock()
        mock_nominatim_class.return_value = mock_geolocator

        loc_padaria = LocationMock(-21.1775, -47.8103)
        loc_cliente = LocationMock(-21.1850, -47.8200)
        mock_geolocator.geocode.side_effect = [loc_padaria, loc_cliente]

        resposta = calcular_taxa_entrega_handler("Rua Visconde de Inhaúma, 1200, Ribeirão Preto")
        
        assert "taxa de entrega fica em R$" in resposta
        assert "A distância calculada" in resposta

    @patch("app.tenants.padaria.tools.Nominatim")
    def test_handler_entrega_acima_do_limite_10km(self, mock_nominatim_class):
        mock_geolocator = MagicMock()
        mock_nominatim_class.return_value = mock_geolocator

        loc_padaria = LocationMock(-21.1775, -47.8103)
        loc_cliente = LocationMock(-23.5505, -46.6333)
        mock_geolocator.geocode.side_effect = [loc_padaria, loc_cliente]

        resposta = calcular_taxa_entrega_handler("Praça da Sé, São Paulo")
        
        assert "ultrapassa o nosso limite de atendimento de 10 km" in resposta

    @patch("app.tenants.padaria.tools.Nominatim")
    def test_handler_endereco_nao_encontrado(self, mock_nominatim_class):
        mock_geolocator = MagicMock()
        mock_nominatim_class.return_value = mock_geolocator

        loc_padaria = LocationMock(-21.1775, -47.8103)
        mock_geolocator.geocode.side_effect = [loc_padaria, None, None]

        resposta = calcular_taxa_entrega_handler("Endereço Qualquer Totalmente Invalido")
        
        assert "Não foi possível localizar o endereço" in resposta
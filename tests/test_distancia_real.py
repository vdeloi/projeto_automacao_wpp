# tests/test_distancia_real.py
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from app.tenants.padaria.tools import geocodificar_com_fallback

def test_distancia_real_ribeirao_preto():
    """
    Testa a geocodificação real e o cálculo de distância linear
    entre dois endereços no município de Ribeirão Preto, SP.
    """
    # 1. Inicializa o cliente do Nominatim com identificador único
    geolocator = Nominatim(user_agent="padaria_teste_integracao_rp")

    # 2. Define os endereços para o teste
    endereco_origem = "Rua Batatais, 12, Ribeirão Preto, SP"
    endereco_destino = "Rua Pedro Giacheto, 184, Ribeirão Preto, SP"

    # 3. Executa a geocodificação com a estratégia de fallback
    loc_origem = geocodificar_com_fallback(geolocator, endereco_origem)
    loc_destino = geocodificar_com_fallback(geolocator, endereco_destino)

    # 4. Validações de integridade (garante que os pontos foram localizados)
    assert loc_origem is not None, f"Não foi possível localizar a origem: {endereco_origem}"
    assert loc_destino is not None, f"Não foi possível localizar o destino: {endereco_destino}"

    ponto_origem = (loc_origem.latitude, loc_origem.longitude)
    ponto_destino = (loc_destino.latitude, loc_destino.longitude)

    # 5. Calcula a distância linear em quilômetros
    distancia_km = geodesic(ponto_origem, ponto_destino).kilometers

    # Exibe os dados calculados no terminal
    print("\n--- RESULTADO DA GEOCODIFICAÇÃO REAL ---")
    print(f"Origem  ({endereco_origem}): Lat {ponto_origem[0]:.4f}, Lon {ponto_origem[1]:.4f}")
    print(f"Destino ({endereco_destino}): Lat {ponto_destino[0]:.4f}, Lon {ponto_destino[1]:.4f}")
    print(f">> Distância Linear Calculada: {distancia_km:.2f} km <<\n")

    # Validação de sanidade: a distância entre dois bairros de Ribeirão Preto deve ser maior que 0 e menor que 30 km
    assert 0.1 < distancia_km < 30.0

if __name__ == "__main__":
    # Permite a execução direta como script
    test_distancia_real_ribeirao_preto()
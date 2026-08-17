# app/tenants/padaria/tools.py
import re
import math
from typing import Optional, Tuple, Any
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from app.tools.base_tool import AppTool

# Endereço base da Padaria Pão Quente em Ribeirão Preto
ENDERECO_PADARIA = "Rua General Osório, 500, Centro, Ribeirão Preto, São Paulo, Brasil"

def calcular_valor_por_distancia(distancia_km: float) -> Tuple[float, bool]:
    """
    Calcula a taxa de entrega com base na distância linear em quilômetros.
    Retorna uma tupla: (valor_em_reais, entrega_permitida).
    """
    if distancia_km < 0:
        return 0.0, False
    if distancia_km <= 0.5:
        return 0.0, True
    elif distancia_km <= 1.0:
        return 7.0, True
    elif distancia_km <= 2.0:
        return 8.0, True
    elif distancia_km <= 3.0:
        return 9.0, True
    elif distancia_km <= 10.0:
        km_adicional = math.ceil(distancia_km - 3.0)
        valor = 9.0 + (km_adicional * 1.0)
        return valor, True
    else:
        return 0.0, False

def _limpar_formatacao_endereco(texto: str) -> str:
    """Remove vírgulas repetidas, espaços extras e normaliza o estado."""
    texto = re.sub(r'\bSP\b', 'São Paulo', texto, flags=re.IGNORECASE)
    texto = re.sub(r'[,\s]*,[,\s]*', ', ', texto)
    texto = re.sub(r'\s+', ' ', texto).strip(' ,')
    return texto

def geocodificar_com_fallback(geolocator: Nominatim, endereco: str) -> Optional[Any]:
    """
    Estratégia de geocodificação progressiva em camadas para máxima resiliência.
    """
    endereco_limpo = _limpar_formatacao_endereco(endereco)

    # 1. Tentativa 1: Endereço completo formatado
    consulta_1 = f"{endereco_limpo}, Brasil"
    loc = geolocator.geocode(consulta_1, timeout=10)
    if loc:
        return loc

    # 2. Tentativa 2: Sem números prediais
    sem_numero = re.sub(r'\b\d+\b', '', endereco_limpo)
    sem_numero = _limpar_formatacao_endereco(sem_numero)
    consulta_2 = f"{sem_numero}, Brasil"
    loc = geolocator.geocode(consulta_2, timeout=10)
    if loc:
        return loc

    # 3. Tentativa 3: Sem prefixos de logradouro
    sem_prefixo = re.sub(r'\b(rua|avenida|av|travessa|alameda|r\.)\b', '', sem_numero, flags=re.IGNORECASE)
    sem_prefixo = _limpar_formatacao_endereco(sem_prefixo)
    consulta_3 = f"{sem_prefixo}, Brasil"
    loc = geolocator.geocode(consulta_3, timeout=10)
    if loc:
        return loc

    # 4. Tentativa 4: Variações fonéticas/ortográficas comuns
    if "giacheto" in sem_prefixo.lower():
        variacao = re.sub(r'giacheto', 'Giachetto', sem_prefixo, flags=re.IGNORECASE)
        loc = geolocator.geocode(f"{variacao}, Brasil", timeout=10)
        if loc:
            return loc

    return None

def calcular_taxa_entrega_handler(endereco_cliente: str) -> str:
    """
    Função handler executada pelo agente Gemini para calcular a taxa de entrega.
    """
    print(f"[TOOL EXECUTADA - PADARIA] Calculando entrega para: {endereco_cliente}")
    try:
        geolocator = Nominatim(user_agent="padaria_pao_quente_wpp_v3")

        loc_padaria = geolocator.geocode(ENDERECO_PADARIA, timeout=10)
        loc_cliente = geocodificar_com_fallback(geolocator, endereco_cliente)

        if not loc_cliente:
            return (
                f"Não foi possível localizar o endereço '{endereco_cliente}'. "
                "Por favor, peça ao cliente para confirmar o nome da rua, bairro ou CEP."
            )

        ponto_padaria = (loc_padaria.latitude, loc_padaria.longitude)
        ponto_cliente = (loc_cliente.latitude, loc_cliente.longitude)

        distancia_km = geodesic(ponto_padaria, ponto_cliente).kilometers
        valor, entrega_disponivel = calcular_valor_por_distancia(distancia_km)

        if not entrega_disponivel:
            return (
                f"A distância calculada até o endereço é de aproximadamente {distancia_km:.2f} km. "
                "Infelizmente este endereço ultrapassa o nosso limite de atendimento de 10 km."
            )

        if valor == 0.0:
            return (
                f"A distância calculada é de {distancia_km:.2f} km. "
                "A taxa de entrega é GRÁTIS para este endereço!"
            )

        return (
            f"A distância calculada até o local é de aproximadamente {distancia_km:.2f} km. "
            f"A taxa de entrega fica em R$ {valor:.2f}."
        )

    except Exception as error:
        print(f"[ERRO GEOPY] Falha ao calcular rota: {error}")
        return "Ocorreu uma instabilidade temporária no serviço de mapas ao consultar o endereço."

# Ferramenta de cálculo de taxa de entrega
tool_calcular_taxa_entrega = AppTool(
    name="calcular_taxa_entrega",
    description="Calcula o valor da taxa de entrega para a Padaria Pão Quente com base no endereço do cliente.",
    parameters={
        "type": "object",
        "properties": {
            "endereco_cliente": {
                "type": "string",
                "description": "Endereço de destino fornecido pelo cliente."
            }
        },
        "required": ["endereco_cliente"]
    },
    handler=calcular_taxa_entrega_handler
)

# Ferramenta de verificação de fornada
def verificar_fornada_handler() -> str:
    return "A próxima fornada de pão francês sai daqui a 10 minutos!"

tool_verificar_fornada = AppTool(
    name="verificar_status_fornada",
    description="Verifica a previsão do horário da próxima fornada de pão quente.",
    parameters={"type": "object", "properties": {}},
    handler=verificar_fornada_handler
)
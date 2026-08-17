# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.core.config import settings
from app.models.chat import ChatRequest, ChatResponse
from app.services.gemini_agent import GeminiInteractionsAgent
from app.services.session_manager import session_manager
from app.tenants.registry import tenant_registry

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Executado ao ligar o servidor
    print("[INICIALIZAÇÃO] Sincronizando RAG dos tenants...")
    tenant_registry.inicializar_todos_os_rags()
    yield
    # Executado ao desligar o servidor
    print("[ENCERRAMENTO] Finalizando aplicação...")

# 1. Cria a aplicação FastAPI com lifespan
app = FastAPI(
    title="Assistente Virtual Multi-Tenant - GenAI",
    version="1.0.0",
    description="Plataforma multi-tenant para atendimento automatizado via WhatsApp.",
    lifespan=lifespan
)

# 2. Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Disponibiliza o Frontend Mock
app.mount("/mock", StaticFiles(directory="mock_frontend", html=True), name="mock")

# 4. Agente Inteligente do Gemini
gemini_agent = GeminiInteractionsAgent(
    api_key=settings.gemini_api_key,
    model_name=settings.model_name
)

@app.get("/", tags=["Health Check"])
def root():
    """Redireciona a raiz para a interface web."""
    return RedirectResponse(url="/mock")

@app.post(
    "/api/v1/chat/mock",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    tags=["WhatsApp Mock"]
)
def process_mock_message(request: ChatRequest) -> ChatResponse:
    try:
        tenant = tenant_registry.get_tenant(request.tenant_id)
        if not tenant:
            return ChatResponse(
                response="Desculpe, o estabelecimento selecionado não foi encontrado.",
                interaction_id=None,
                status="error"
            )

        previous_id = session_manager.get_last_interaction_id(
            tenant_id=request.tenant_id,
            phone_number=request.phone_number
        )

        gemini_agent.system_instruction = tenant.system_instruction

        agent_response = gemini_agent.generate_interaction(
            user_input=request.message,
            previous_interaction_id=previous_id,
            tool_schemas=tenant.get_all_tool_schemas(),
            tool_map=tenant.get_tool_map()
        )

        if agent_response.interaction_id:
            session_manager.save_interaction_id(
                tenant_id=request.tenant_id,
                phone_number=request.phone_number,
                interaction_id=agent_response.interaction_id
            )

    except Exception as error:
        print(f"[ERRO NO PROCESSAMENTO] Falha no endpoint: {error}")
        return ChatResponse(
            response="Ocorreu um erro temporário ao processar o seu atendimento.",
            interaction_id=None,
            status="error"
        )
    else:
        return ChatResponse(
            response=agent_response.text_output,
            interaction_id=agent_response.interaction_id,
            status="success"
        )
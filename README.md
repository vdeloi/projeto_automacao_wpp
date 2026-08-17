

```markdown
# 🤖 Assistente Virtual Multi-Tenant para WhatsApp (Google GenAI)

Uma plataforma profissional, modular, altamente escalável e resiliente para automação de atendimento via WhatsApp utilizando inteligência artificial generativa com a SDK oficial **`google-genai`** (Interactions API).

A aplicação foi projetada utilizando princípios de **Programação Orientada a Objetos (POO)**, **Clean Architecture** e **Design Multi-Tenant**, permitindo atender centenas de estabelecimentos simultaneamente (clínicas odontológicas, lojas, padarias) e milhares de clientes finais de forma concorrente e isolada.

---

## 🏗️ Pilares de Arquitetura & Escalabilidade

### 1. 🏢 Arquitetura Multi-Tenant (Multi-Empresas)
A aplicação é nativamente preparada para servir múltiplos estabelecimentos em um único servidor:
- **Ferramentas Isoladas (Tools):** Cada empresa possui o seu próprio conjunto de ações executáveis (ex: agendamento em clínica vs. pedido em restaurante).
- **RAGs Isolados (Base de Conhecimento):** As buscas de arquivos e manuais de FAQ são delimitadas estritamente ao repositório de documentos do comércio correspondente.
- **Banco de Dados Segregado:** Dados de clientes e histórico de agendamentos são armazenados com isolamento lógico por empresa.

### 2. ⚡ Concorrência & Isolamento de Clientes (`Interactions API`)
Cada cliente que envia uma mensagem no WhatsApp ganha uma sessão de interação única no Gemini:
- **Foco Total no Atendimento:** O modelo não compartilha contexto entre diferentes clientes. Toda chamada utiliza um `interaction_id` dedicado para resgatar a memória do atendimento individual.
- **Eficiência de Tokens e Custo:** O uso de estado no servidor (`previous_interaction_id`) eleva a taxa de cache hit, reduzindo drasticamente os custos operacionais por mensagem.

### 3. 🛡️ Resiliência e Código Defensivo (`try / except / else / finally`)
O código-fonte segue o padrão estrito de tratamento de exceções em todas as camadas da aplicação (API, Chamadas da LLM, Banco de Dados):
- **Blocos `try`:** Para execução segura de chamadas de rede e processamento.
- **Blocos `except`:** Captura e log detalhado de falhas sem interromper o serviço.
- **Blocos `else`:** Executados apenas em caso de sucesso absoluto da operação.
- **Garantia de Uptime:** Erros de comunicação com APIs externas retornam mensagens amigáveis ao cliente do WhatsApp sem crashar a API FastAPI.

---

## 🚀 Funcionalidades Principais

- 🧠 **Inteligência com Gemini Interactions API:** Respostas naturais, contextuais e com suporte a conversas multiturno.
- 🛠️ **Tool Use (Chamada de Funções):** Execução de ações em tempo real (ex: agendar consultas, verificar estoque, registrar reclamações).
- 📚 **RAG (Managed File Search):** Consulta dinâmica a documentos e Manuais de Instrução/FAQ específicos do estabelecimento.
- 📱 **Interface Mock do WhatsApp Web:** Frontend local em HTML/JS simulando o WhatsApp Web para testes rápidos e sem custos antes da migração.
- 🔌 **Pronto para Meta Cloud API & AWS:** Estrutura preparada para migração transparente para os servidores oficiais da Meta e deploy em ambiente de nuvem AWS (ECS/Lambda).

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.11+
- **IA & LLM:** `google-genai` (Interactions API `>= 2.3.0`)
- **Backend & API:** FastAPI, Uvicorn
- **Validação de Dados:** Pydantic v2, Pydantic Settings
- **Banco de Dados (ORM):** SQLModel / SQLAlchemy (SQLite local / PostgreSQL na nuvem)
- **Frontend Mock:** HTML5, CSS3, JavaScript ES6 (Fetch API)

---

## 📁 Estrutura do Projeto

```text
projeto_automacao_wpp/
│
├── .env.example          # Modelo de variáveis de ambiente
├── .gitignore            # Arquivos e pastas ignorados pelo Git
├── README.md             # Documentação e arquitetura do projeto
├── requirements.txt      # Dependências da aplicação
│
├── app/                  # Código-fonte principal
│   ├── main.py           # Ponto de entrada do FastAPI
│   ├── core/             # Configurações globais e inicialização segura
│   ├── services/         # Regras de negócio, Gemini Interactions Agent e RAG
│   ├── tools/            # Ferramentas acionáveis pelo modelo (Tool Use)
│   ├── models/           # Schemas de dados Pydantic e tabelas do banco
│   └── api/              # Endpoints HTTP e Webhooks
│
├── data/                 # Armazenamento local (PDFs para RAG e Banco SQLite)
└── mock_frontend/        # Interface web para simular o WhatsApp
    └── index.html

```

---

## 🔧 Configuração e Instalação

### Pré-requisitos

* **Python 3.11** ou superior instalado.
* Chave de API do **Google AI Studio** (`GEMINI_API_KEY`).

### 1. Acessar o Repositório

```bash
cd projeto_automacao_wpp

```

### 2. Criar e Ativar o Ambiente Virtual (`venv`)

```bash
# No Windows (Command Prompt)
python -m venv venv
venv\Scripts\activate

# No Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# No Linux/Mac
source venv/bin/activate

```

### 3. Instalar as Dependências

```bash
pip install -r requirements.txt

```

### 4. Configurar as Variáveis de Ambiente

Crie um arquivo chamado `.env` na raiz do projeto (baseando-se no `.env.example`) e insira a sua chave de API:

```ini
GEMINI_API_KEY=sua_chave_aqui_sem_aspas
ENVIRONMENT=development
PORT=8000

```

---

## 🧪 Como Executar e Testar

### 1. Iniciar o Backend (FastAPI)

Com o `venv` ativado, execute no terminal:

```bash
uvicorn app.main:app --reload

```

A API estará rodando em: `http://127.0.0.1:8000`

Documentação Swagger interativa: `http://127.0.0.1:8000/docs`

### 2. Testar no WhatsApp Mock

1. Abra o arquivo `mock_frontend/index.html` diretamente no seu navegador.
2. Digite uma mensagem na caixa de texto para interagir com o assistente do Gemini em tempo real!

---

## 📋 Roadmap de Desenvolvimento

* [x] Estrutura inicial do projeto e Clean Architecture
* [x] Frontend Mock do WhatsApp Web
* [x] Definição de Abstração POO para o Gemini (`BaseLLMAgent` e `GeminiInteractionsAgent`)
* [x] Atualização do README com foco em Multi-Tenancy e Escalabilidade
* [x] Configuração de leitura segura do `.env` com Pydantic (`app/core/config.py`) com blocos `try/else`
* [ ] Implementação do gerenciador Multi-Tenant de empresas/sessões
* [ ] Implementação de RAG com busca em arquivos gerenciados
* [ ] Criação de Tools dinâmicas por nicho (Clínicas, Padarias)
* [ ] Integração com a Meta Cloud API (WhatsApp Oficial)
* [ ] Implantação escalável na AWS

```
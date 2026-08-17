# app/services/gemini_agent.py
import time
from typing import Any, Dict, List, Optional
from google import genai
from app.services.base_agent import BaseLLMAgent, AgentResponse
from app.tools.base_tool import AppTool

class GeminiInteractionsAgent(BaseLLMAgent):
    """
    Agente inteligente com suporte a ciclo completo de Function Calling e RAG.
    """
    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-3.5-flash-lite",
        system_instruction: Optional[str] = None
    ) -> None:
        super().__init__(model_name=model_name, system_instruction=system_instruction)
        self.client = genai.Client(api_key=api_key)

    def _extract_text_from_interaction(self, raw_response: Any) -> str:
        """
        Extrai o texto final gerado pelo modelo a partir dos steps da resposta.
        """
        if not raw_response:
            return "Olá! Como posso ajudar você hoje?"

        # 1. Tenta pegar direto do output_text caso preenchido
        if hasattr(raw_response, "output_text") and raw_response.output_text:
            return str(raw_response.output_text).strip()

        # 2. Tenta pegar do atributo text
        if hasattr(raw_response, "text") and raw_response.text:
            return str(raw_response.text).strip()

        textos: List[str] = []
        steps = getattr(raw_response, "steps", []) or []

        # 3. Percorre todos os passos em busca do model_output
        for step in steps:
            step_type = str(getattr(step, "type", "")).lower()

            if "thought" in step_type:
                continue

            # Se houver texto direto no step
            if hasattr(step, "text") and step.text:
                textos.append(str(step.text).strip())

            # Se houver blocos de conteúdo estruturados
            content = getattr(step, "content", None)
            if content:
                blocks = content if isinstance(content, list) else [content]
                for block in blocks:
                    block_type = str(getattr(block, "type", "")).lower()
                    if "thought" in block_type:
                        continue

                    if hasattr(block, "text") and block.text:
                        textos.append(str(block.text).strip())
                    elif isinstance(block, dict) and block.get("text"):
                        textos.append(str(block["text"]).strip())

                    # Exibe citações do RAG no terminal caso existam
                    annotations = getattr(block, "annotations", []) or []
                    for annotation in annotations:
                        annot_type = str(getattr(annotation, "type", "")).lower()
                        if "citation" in annot_type:
                            nome_arq = getattr(annotation, "file_name", "documento")
                            pag = getattr(annotation, "page_number", None)
                            print(f"[RAG CITAÇÃO] Arquivo: {nome_arq}" + (f" | Pág: {pag}" if pag else ""))

        if textos:
            return "\n".join([t for t in textos if t]).strip()

        return "Desculpe, não consegui processar a resposta completa. Poderia repetir?"

    def generate_interaction(
        self,
        user_input: str,
        previous_interaction_id: Optional[str] = None,
        tool_schemas: Optional[List[Dict[str, Any]]] = None,
        tool_map: Optional[Dict[str, AppTool]] = None,
        store: bool = True,
        max_turns: int = 5,
        **kwargs: Any
    ) -> AgentResponse:
        """
        Executa o ciclo completo de interação até que o modelo conclua as respostas.
        """
        inicio_total = time.perf_counter()
        tools_executed: List[str] = []
        current_id = previous_interaction_id

        # Configuração da chamada inicial
        interaction_kwargs: Dict[str, Any] = {
            "model": self.model_name,
            "input": user_input,
            "store": store,
        }

        if previous_interaction_id:
            interaction_kwargs["previous_interaction_id"] = previous_interaction_id
        if self.system_instruction:
            interaction_kwargs["system_instruction"] = self.system_instruction
        if tool_schemas:
            interaction_kwargs["tools"] = tool_schemas

        try:
            # 1. Primeira chamada ao Gemini
            t0 = time.perf_counter()
            raw_response = self.client.interactions.create(**interaction_kwargs)
            t1 = time.perf_counter()
            print(f"[PERFORMANCE] Chamada Gemini: {t1 - t0:.2f}s")
            current_id = getattr(raw_response, "id", current_id)

            # 2. Laço para resolução de ferramentas enquanto o status exigir ação
            turn_count = 0
            while turn_count < max_turns:
                steps = getattr(raw_response, "steps", []) or []
                status = getattr(raw_response, "status", None)

                # Identifica se existem chamadas de funções pendentes
                function_call_steps = [
                    s for s in steps if "function_call" in str(getattr(s, "type", "")).lower()
                ]

                # Se não há ferramentas para rodar e o status não requer ação, finalizamos
                if not function_call_steps and status != "requires_action":
                    break

                if not tool_map:
                    break

                function_results = []
                t_tool_inicio = time.perf_counter()

                for fc_step in function_call_steps:
                    func_name = getattr(fc_step, "name", None)
                    func_args = getattr(fc_step, "arguments", {}) or {}
                    call_id = getattr(fc_step, "id", None)

                    if func_name in tool_map:
                        tools_executed.append(func_name)
                        app_tool = tool_map[func_name]
                        
                        # Executa a função Python local
                        resultado_execucao = app_tool.execute(**func_args)

                        # Formato compatível com a Interactions API
                        function_results.append({
                            "type": "function_result",
                            "name": func_name,
                            "call_id": call_id,
                            "result": {
                                "output": str(resultado_execucao)
                            }
                        })

                t_tool_fim = time.perf_counter()
                print(f"[PERFORMANCE] Execução Tool Local: {(t_tool_fim - t_tool_inicio) * 1000:.2f}ms")

                if not function_results:
                    break

                # Envia o resultado da execução de volta ao Gemini
                t2 = time.perf_counter()
                raw_response = self.client.interactions.create(
                    model=self.model_name,
                    input=function_results,
                    previous_interaction_id=current_id,
                    tools=tool_schemas,
                    store=store
                )
                t3 = time.perf_counter()
                print(f"[PERFORMANCE] Chamada Gemini (Resposta Final): {t3 - t2:.2f}s")
                current_id = getattr(raw_response, "id", current_id)
                turn_count += 1

        except Exception as error:
            print(f"[ERRO GENAI] Falha no processamento: {error}")
            return AgentResponse(
                text_output="Desculpe, ocorreu uma instabilidade temporária ao consultar as informações.",
                interaction_id=previous_interaction_id,
                tools_called=tools_executed,
                raw_response=None
            )
        else:
            output_text = self._extract_text_from_interaction(raw_response)
            fim_total = time.perf_counter()
            print(f"[PERFORMANCE] TEMPO TOTAL: {fim_total - inicio_total:.2f}s\n")
            return AgentResponse(
                text_output=output_text,
                interaction_id=current_id,
                tools_called=tools_executed,
                raw_response=raw_response
            )
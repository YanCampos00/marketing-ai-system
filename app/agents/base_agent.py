import json 
from app.core.llm_service import gerar_conteudo_com_llm

class Agent:
    def __init__(self, name, instructions_template, data_tool_function, llm_model):
        self.name = name
        self.instructions_template = instructions_template
        self.data_tool_function = data_tool_function 
        self.llm_model = llm_model
        print(f"Agente '{self.name}' inicializado.")

    def _parse_llm_response(self, llm_text_response, kpis_json=None):
        """
        Para agentes de plataforma, retorna diretamente o kpis_json já salvo/calculado.
        Para análise textual, mantém a extração dos delimitadores se necessário.
        """
        analise_textual = None

        text_start_delim = "--- INÍCIO ANÁLISE TEXTUAL ---"
        text_end_delim = "--- FIM ANÁLISE TEXTUAL ---"

        try:
            start_index_text = llm_text_response.find(text_start_delim)
            end_index_text = llm_text_response.find(text_end_delim)

            if start_index_text != -1 and end_index_text != -1:
                analise_textual = llm_text_response[start_index_text + len(text_start_delim):end_index_text].strip()
            elif start_index_text != -1:
                analise_textual = llm_text_response[start_index_text + len(text_start_delim):].strip()
                print(f"   [Base Agent - {self.name}] Delimitador final da análise textual não encontrado, pegando até o fim.")
            else:
                print(f"   [Base Agent - {self.name}] Delimitadores da análise textual não encontrados na resposta do LLM.")
                analise_textual = llm_text_response

        except Exception as e_parse:
            print(f"   [Base Agent - {self.name}] Erro inesperado ao parsear análise textual do LLM: {e_parse}")
            analise_textual = llm_text_response

        return {"kpis_json": kpis_json, "analise_textual": analise_textual}

    def run(self, gspread_client, tool_input_params, cliente_contexto=None, 
            mes_analise_atual_param=None, extra_tool_params=None, kpis_json=None, caminho_json=None):
        print(f"\n--- Executando {self.name} ---")
        
        processed_data_for_prompt = None
        if self.name == "Agente Orquestrador": # Renomeado de 'Agente Manager Estratégico'
            if not extra_tool_params:
                error_message = f"Erro Crítico para {self.name}: extra_tool_params não fornecido."
                print(error_message)
                return {"llm_response_manager": error_message, "data_markdown": "Parâmetros extras não fornecidos."}
            processed_data_for_prompt = self.data_tool_function(extra_tool_params)
        else:
            if gspread_client is None and self.name == "Agente de Mídia": # Agente genérico
                error_message = f"Erro Crítico para {self.name}: gspread_client não fornecido."
                print(error_message)
                return {
                    "kpis_json": None,
                    "analise_textual": error_message,
                    "data_markdown": "Cliente gspread não fornecido.",
                    "caminho_json": None
                }
            
            processed_data_for_prompt = self.data_tool_function(
                gspread_client, tool_input_params, mes_analise_atual_param
            )
            # Se for agente de plataforma, extraia só o markdown
            if self.name == "Agente de Mídia" and isinstance(processed_data_for_prompt, dict):
                markdown_only = processed_data_for_prompt.get("markdown")
                caminho_json = processed_data_for_prompt.get("caminho_json")
                processed_data_for_prompt = markdown_only

        is_error_in_data = False
        if processed_data_for_prompt is None:
            is_error_in_data = True
            processed_data_for_prompt = "Erro: Falha ao obter ou processar dados (retorno None da data_tool_function)."
        elif isinstance(processed_data_for_prompt, str) and \
             (processed_data_for_prompt.startswith("ErroDados_") or 
              processed_data_for_prompt.startswith("ErroInesperado_") or
              "Erro:" in processed_data_for_prompt):
            is_error_in_data = True
        
        data_markdown_log = processed_data_for_prompt

        if is_error_in_data:
            error_message_data = f"Não foi possível obter ou processar dados para {self.name}. Detalhe: {processed_data_for_prompt}"
            print(error_message_data)
            if self.name == "Agente Orquestrador":
                return {"llm_response_manager": processed_data_for_prompt, "data_markdown": data_markdown_log}
            else:
                return {
                    "kpis_json": None,
                    "analise_textual": processed_data_for_prompt,
                    "data_markdown": data_markdown_log,
                    "caminho_json": None
                }

        if not self.llm_model:
            error_message_llm_init = f"Erro Crítico para {self.name}: Modelo LLM não inicializado."
            print(error_message_llm_init)
            if self.name == "Agente Orquestrador":
                return {"llm_response_manager": error_message_llm_init, "data_markdown": data_markdown_log}
            else:
                return {
                    "kpis_json": None,
                    "analise_textual": error_message_llm_init,
                    "data_markdown": data_markdown_log,
                    "caminho_json": None
                }

        if "ERRO DE CARREGAMENTO DE PROMPT" in self.instructions_template or not self.instructions_template.strip():
            error_message_template = f"Erro Crítico para {self.name}: Template de instruções não carregado ou vazio."
            print(error_message_template)
            if self.name == "Agente Orquestrador":
                return {"llm_response_manager": error_message_template, "data_markdown": data_markdown_log}
            else:
                return {
                    "kpis_json": None,
                    "analise_textual": error_message_template,
                    "data_markdown": data_markdown_log,
                    "caminho_json": None
                }

        prompt_final = ""
        try:
            if self.name == "Agente Orquestrador":
                if not isinstance(processed_data_for_prompt, dict):
                    error_msg = f"Input para {self.name} não é um dicionário como esperado: {processed_data_for_prompt}"
                    print(f"   [Base Agent - {self.name}] {error_msg}")
                    return {"llm_response_manager": error_msg, "data_markdown": data_markdown_log}
                
                params_para_formatar_manager = processed_data_for_prompt.copy()
                if 'cliente_contexto' not in params_para_formatar_manager:
                    params_para_formatar_manager['cliente_contexto'] = cliente_contexto if cliente_contexto else "Contexto do cliente não fornecido."
                prompt_final = self.instructions_template.format(**params_para_formatar_manager)
            else:
                prompt_final = self.instructions_template.format(
                    cliente_contexto=cliente_contexto if cliente_contexto else "Contexto do cliente não fornecido.",
                    dados_markdown=processed_data_for_prompt,
                    plataforma=tool_input_params.get('plataforma', 'Mídia Paga') # Adiciona a plataforma
                )
        except KeyError as e:
            error_message_format = f"Erro ao formatar o prompt para {self.name}: Chave {e} não encontrada."
            print(error_message_format)
            if self.name == "Agente Orquestrador":
                return {"llm_response_manager": error_message_format, "data_markdown": data_markdown_log}
            else:
                return {
                    "kpis_json": None,
                    "analise_textual": error_message_format,
                    "data_markdown": data_markdown_log,
                    "caminho_json": None
                }
        except Exception as e_format_inesperado:
            error_message_format_inesperado = f"Erro inesperado ao formatar o prompt para {self.name}: {e_format_inesperado}"
            print(error_message_format_inesperado)
            if self.name == "Agente Orquestrador":
                return {"llm_response_manager": error_message_format_inesperado, "data_markdown": data_markdown_log}
            else:
                return {
                    "kpis_json": None,
                    "analise_textual": error_message_format_inesperado,
                    "data_markdown": data_markdown_log,
                    "caminho_json": None
                }

        llm_raw_response_text = ""
        try:
            is_json_task = self.name == "Agente de Mídia"
            llm_raw_response_text = gerar_conteudo_com_llm(
                self.llm_model, 
                prompt_final,
                is_json_extraction_task=is_json_task
            )
            
            if isinstance(llm_raw_response_text, str) and llm_raw_response_text.startswith("Erro:"):
                print(f"   [Base Agent - {self.name}] Erro retornado pelo llm_service: {llm_raw_response_text}")
                if self.name == "Agente de Mídia":
                    return {
                        "kpis_json": None,
                        "analise_textual": llm_raw_response_text,
                        "raw_llm_response": llm_raw_response_text,
                        "data_markdown": data_markdown_log,
                        "caminho_json": caminho_json
                    }
                else:
                    return {"llm_response_manager": llm_raw_response_text, "data_markdown": data_markdown_log}

            if self.name == "Agente de Mídia":
                parsed_output = self._parse_llm_response(llm_raw_response_text, kpis_json=kpis_json)
                return {
                    "kpis_json": parsed_output["kpis_json"],
                    "analise_textual": parsed_output["analise_textual"],
                    "raw_llm_response": llm_raw_response_text,
                    "data_markdown": data_markdown_log,
                    "caminho_json": caminho_json
                }
            else:
                return {
                    "llm_response_manager": llm_raw_response_text,
                    "data_markdown": data_markdown_log
                }

        except Exception as e_llm_call: 
            error_message_llm_call = f"Erro na chamada ao LLM para {self.name} (após tentativas): {e_llm_call}"
            print(error_message_llm_call)
            if self.name == "Agente Orquestrador":
                 return {"llm_response_manager": error_message_llm_call, "data_markdown": data_markdown_log}
            else:
                return {
                    "kpis_json": None,
                    "analise_textual": error_message_llm_call,
                    "raw_llm_response": llm_raw_response_text,
                    "data_markdown": data_markdown_log,
                    "caminho_json": caminho_json
                }

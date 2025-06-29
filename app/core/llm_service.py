import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.config.config_loader import carregar_config_global # Para buscar configs de retry

# Carrega configurações globais para retry
global_config_llm_service = carregar_config_global()
if global_config_llm_service is None:
    print("LLM SERVICE: Falha ao carregar config global, usando retries padrão.")
    RETRY_ATTEMPTS = 3
    RETRY_WAIT_MULTIPLIER = 1
    RETRY_WAIT_MIN_SECONDS = 2
    RETRY_WAIT_MAX_SECONDS = 10
else:
    retry_params = global_config_llm_service.get("retry_config", {})
    RETRY_ATTEMPTS = retry_params.get("attempts", 3)
    RETRY_WAIT_MULTIPLIER = retry_params.get("wait_multiplier", 1)
    RETRY_WAIT_MIN_SECONDS = retry_params.get("wait_min_seconds", 2)
    RETRY_WAIT_MAX_SECONDS = retry_params.get("wait_max_seconds", 10)

@retry(
    stop=stop_after_attempt(RETRY_ATTEMPTS),
    wait=wait_exponential(multiplier=RETRY_WAIT_MULTIPLIER, min=RETRY_WAIT_MIN_SECONDS, max=RETRY_WAIT_MAX_SECONDS),
    retry=retry_if_exception_type(Exception) # ATENÇÃO: Refinar os tipos de exceção
)
def gerar_conteudo_com_llm(llm_model, prompt_text, is_json_extraction_task=False):
    """
    Gera conteúdo usando o modelo LLM fornecido, com lógica de retentativa
    e configuração de temperatura ajustável.
    
    Args:
        llm_model: Instância do modelo LLM.
        prompt_text (str): O prompt a ser enviado.
        is_json_extraction_task (bool): True se a tarefa principal for extrair JSON,
                                         para usar temperatura baixa. False caso contrário.
                                         
    Returns:
        str: A resposta textual do LLM.
    """
    if not llm_model:
        raise ValueError("Erro Crítico no llm_service: Modelo LLM não fornecido.")
    if not prompt_text:
        raise ValueError("Erro Crítico no llm_service: Prompt vazio fornecido.")
        
    print(f"   [LLM Service] Enviando prompt: {prompt_text[:100]}...")

    temperatura_configurada = 0.1 if is_json_extraction_task else 0.7

    generation_config_params = {
        "temperature": temperatura_configurada
    }
    if is_json_extraction_task and temperatura_configurada == 0.1:
        generation_config_params["top_k"] = 1

    generation_config = genai.types.GenerationConfig(**generation_config_params)

    try:
        response = llm_model.generate_content(
            prompt_text,
            generation_config=generation_config
        )
        
        if response.prompt_feedback and response.prompt_feedback.block_reason:
            block_reason_message = f"Prompt bloqueado. Razão: {response.prompt_feedback.block_reason}"
            if response.prompt_feedback.block_reason_message:
                 block_reason_message += f" - {response.prompt_feedback.block_reason_message}"
            print(f"   [LLM Service] {block_reason_message}")
            return f"Erro: Prompt bloqueado pela API. Razão: {response.prompt_feedback.block_reason}"

        if not response.candidates or not response.text:
            safety_ratings_str = "N/A"
            if response.candidates and response.candidates[0].safety_ratings:
                safety_ratings_str = ", ".join([f"{sr.category}: {sr.probability.name}" for sr in response.candidates[0].safety_ratings])
            error_message = f"Resposta do LLM vazia ou inválida. Possível problema de segurança ou filtro de conteúdo. Safety Ratings: {safety_ratings_str}"
            print(f"   [LLM Service] {error_message}")
            return f"Erro: {error_message}"

        print("   [LLM Service] Resposta recebida do LLM.")
        return response.text
    except Exception as e:
        print(f"   [LLM Service] Erro após tentativas de chamada à API LLM: {e}")
        raise

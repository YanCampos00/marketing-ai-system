from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """
    Classe base abstrata para todos os agentes.
    Define a estrutura que todos os agentes devem seguir.
    """
    def __init__(self, llm_service):
        self.llm_service = llm_service

    @abstractmethod
    def run(self, **kwargs):
        """
        Método principal que executa a lógica do agente.
        Deve ser implementado por todas as subclasses.
        """
        pass
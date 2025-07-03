from abc import ABC, abstractmethod
import pandas as pd

class BaseConnector(ABC):
    """
    Classe base abstrata (interface) para conectores de dados.
    Define o contrato que todos os conectores de dados devem seguir.
    """
    @abstractmethod
    def get_data(self, data_source: str, client_config: dict, mes_analise: str) -> pd.DataFrame:
        """
        Método principal que busca dados de uma fonte específica.
        Deve ser implementado por todas as subclasses.

        Args:
            data_source (str): A fonte dos dados (ex: 'google_ads', 'meta_ads').
            client_config (dict): A configuração do cliente.
            mes_analise (str): O mês da análise no formato 'AAAA-MM-DD'.

        Returns:
            pd.DataFrame: Um DataFrame do pandas com os dados extraídos.
        """
        pass

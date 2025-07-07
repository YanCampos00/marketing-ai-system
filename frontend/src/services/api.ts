
import axios from 'axios';
import { toast } from 'react-toastify';

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Adiciona um interceptador de resposta para tratar erros globalmente
api.interceptors.response.use(
  (response) => response,
  (error) => {
    let errorMessage = 'Ocorreu um erro inesperado.';

    if (error.response && error.response.data && error.response.data.detail) {
      const errorDetail = error.response.data.detail;

      if (typeof errorDetail === 'object' && errorDetail.message) {
        // Estrutura de erro customizada: { message: string, details: [] }
        errorMessage = errorDetail.message;
        if (errorDetail.details && Array.isArray(errorDetail.details) && errorDetail.details.length > 0) {
          const detailsText = errorDetail.details.join('; ');
          errorMessage += `: ${detailsText}`;
        }
      } else if (typeof errorDetail === 'string') {
        // Estrutura de erro padrão da FastAPI
        errorMessage = errorDetail;
      }
    } else if (error.message) {
      errorMessage = error.message;
    }

    toast.error(errorMessage, { autoClose: 8000 }); // Aumenta o tempo de exibição para erros detalhados

    return Promise.reject(error);
  }
);

export default api;

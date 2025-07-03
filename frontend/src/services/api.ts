
import axios from 'axios';
import { toast } from 'react-toastify'; // Importa o toast

// A URL base da API é lida da variável de ambiente VITE_API_BASE_URL.
// O Vite substitui `import.meta.env.VITE_API_BASE_URL` em tempo de build.
// Fornecemos um valor padrão para o caso de a variável não estar definida.
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
    const message = error.response?.data?.detail || error.message || 'Ocorreu um erro inesperado.';
    toast.error(message);
    return Promise.reject(error);
  }
);

export default api;

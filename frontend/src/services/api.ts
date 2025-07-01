
import axios from 'axios';

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

export default api;

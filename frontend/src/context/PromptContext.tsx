import React, { createContext, useState, useEffect, useCallback, ReactNode, useContext } from 'react';
import api from '../services/api';
import { toast } from 'react-toastify';

interface Prompt {
  id: string;
  nome: string;
  conteudo: string;
  descricao?: string;
}

interface PromptContextType {
  prompts: Prompt[];
  loading: boolean;
  error: string | null;
  fetchPrompts: () => Promise<void>;
  updatePrompt: (promptName: string, promptData: Partial<Prompt>) => Promise<void>;
}

const PromptContext = createContext<PromptContextType | undefined>(undefined);

export const PromptProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPrompts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get<Prompt[]>('/prompts');
      setPrompts(response.data);
    } catch (err: any) {
      setError('Erro ao carregar prompts.');
      toast.error(`Erro ao carregar prompts: ${err.response?.data?.detail || err.message}`);
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  const updatePrompt = useCallback(async (promptName: string, promptData: Partial<Prompt>) => {
    try {
      await api.put(`/prompts/${promptName}`, promptData);
      toast.success('Prompt atualizado com sucesso!');
      await fetchPrompts();
    } catch (err: any) {
      toast.error(`Erro ao atualizar prompt: ${err.response?.data?.detail || err.message}`);
      console.error(err);
      throw err;
    }
  }, [fetchPrompts]);

  useEffect(() => {
    fetchPrompts();
  }, [fetchPrompts]);

  return (
    <PromptContext.Provider value={{ prompts, loading, error, fetchPrompts, updatePrompt }}>
      {children}
    </PromptContext.Provider>
  );
};

export const usePrompt = () => {
  const context = useContext(PromptContext);
  if (context === undefined) {
    throw new Error('usePrompt must be used within a PromptProvider');
  }
  return context;
};

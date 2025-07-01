import React, { createContext, useState, useEffect, useCallback, ReactNode, useContext } from 'react';
import api from '../services/api';
import * as Types from '../types';
import { toast } from 'react-toastify';

interface ClientContextType {
  clients: Types.Client[];
  loading: boolean;
  error: string | null;
  fetchClients: () => Promise<void>;
  addClient: (client: Types.Client) => Promise<void>;
  updateClient: (clientId: string, clientData: Partial<Types.Client>) => Promise<void>;
  deleteClient: (clientId: string) => Promise<void>;
}

const ClientContext = createContext<ClientContextType | undefined>(undefined);

export const ClientProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [clients, setClients] = useState<Types.Client[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchClients = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get<{ [key: string]: Types.Client }>('/clients');
      setClients(Object.values(response.data));
    } catch (err: any) {
      setError('Erro ao carregar clientes.');
      toast.error(`Erro ao carregar clientes: ${err.response?.data?.detail || err.message}`);
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  const addClient = useCallback(async (client: Types.Client) => {
    try {
      await api.post('/clients', client);
      toast.success('Cliente adicionado com sucesso!');
      await fetchClients();
    } catch (err: any) {
      toast.error(`Erro ao adicionar cliente: ${err.response?.data?.detail || err.message}`);
      console.error(err);
      throw err; // Re-throw para que o componente chamador possa lidar com o erro
    }
  }, [fetchClients]);

  const updateClient = useCallback(async (clientId: string, clientData: Partial<Types.Client>) => {
    try {
      await api.put(`/clients/${clientId}`, clientData);
      toast.success('Cliente atualizado com sucesso!');
      await fetchClients();
    } catch (err: any) {
      toast.error(`Erro ao atualizar cliente: ${err.response?.data?.detail || err.message}`);
      console.error(err);
      throw err;
    }
  }, [fetchClients]);

  const deleteClient = useCallback(async (clientId: string) => {
    try {
      await api.delete(`/clients/${clientId}`);
      toast.success('Cliente excluído com sucesso!');
      await fetchClients();
    } catch (err: any) {
      toast.error(`Erro ao excluir cliente: ${err.response?.data?.detail || err.message}`);
      console.error(err);
      throw err;
    }
  }, [fetchClients]);

  useEffect(() => {
    fetchClients();
  }, [fetchClients]);

  return (
    <ClientContext.Provider value={{ clients, loading, error, fetchClients, addClient, updateClient, deleteClient }}>
      {children}
    </ClientContext.Provider>
  );
};

export const useClient = () => {
  const context = useContext(ClientContext);
  if (context === undefined) {
    throw new Error('useClient must be used within a ClientProvider');
  }
  return context;
};

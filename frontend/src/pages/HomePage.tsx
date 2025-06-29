import React, { useEffect, useState, useCallback } from 'react';
import api from '../services/api';
import * as Types from '../types';
import AnalysisModal from '../components/AnalysisModal';
import AddClientModal from '../components/AddClientModal';
import EditClientModal from '../components/EditClientModal';
import DeleteClientModal from '../components/DeleteClientModal';
import ReportViewerModal from '../components/ReportViewerModal';
import { toast } from 'react-toastify';

const HomePage: React.FC = () => {
  const [clients, setClients] = useState<Types.Client[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isAnalysisInProgress, setIsAnalysisInProgress] = useState<boolean>(false); // Novo estado

  // Estados para os modais
  const [showAnalysisModal, setShowAnalysisModal] = useState<boolean>(false);
  const [showAddClientModal, setShowAddClientModal] = useState<boolean>(false);
  const [showEditClientModal, setShowEditClientModal] = useState<boolean>(false);
  const [showDeleteClientModal, setShowDeleteClientModal] = useState<boolean>(false);
  const [showReportViewerModal, setShowReportViewerModal] = useState<boolean>(false);

  const [selectedClient, setSelectedClient] = useState<Types.Client | null>(null);
  const [analysisCompletedClient, setAnalysisCompletedClient] = useState<string | null>(null);
  const [analysisCompletedMonth, setAnalysisCompletedMonth] = useState<string | null>(null);

  const fetchClients = useCallback(async () => {
    try {
      const response = await api.get<{ [key: string]: Types.Client }>('/clients');
      const clientsArray = Object.values(response.data);
      setClients(clientsArray);
    } catch (err) {
      setError('Erro ao carregar clientes.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchClients();
  }, [fetchClients]);

  // Funções para abrir/fechar modais
  const handleShowAnalysisModal = (client: Types.Client) => {
    setSelectedClient(client);
    setShowAnalysisModal(true);
  };

  const handleCloseAnalysisModal = () => {
    setShowAnalysisModal(false);
    setSelectedClient(null);
  };

  const handleShowAddClientModal = () => setShowAddClientModal(true);
  const handleCloseAddClientModal = () => {
    setShowAddClientModal(false);
    fetchClients(); // Recarrega clientes após adicionar
  };

  const handleShowEditClientModal = (client: Types.Client) => {
    setSelectedClient(client);
    setShowEditClientModal(true);
  };
  const handleCloseEditClientModal = () => {
    setShowEditClientModal(false);
    setSelectedClient(null);
    fetchClients(); // Recarrega clientes após editar
  };

  const handleShowDeleteClientModal = (client: Types.Client) => {
    setSelectedClient(client);
    setShowDeleteClientModal(true);
  };
  const handleCloseDeleteClientModal = () => {
    setShowDeleteClientModal(false);
    setSelectedClient(null);
    fetchClients(); // Recarrega clientes após excluir
  };

  const handleShowReportViewerModal = (clientId?: string, mesAnalise?: string) => {
    setAnalysisCompletedClient(clientId || null);
    setAnalysisCompletedMonth(mesAnalise || null);
    setShowReportViewerModal(true);
  };

  const handleCloseReportViewerModal = () => {
    setShowReportViewerModal(false);
    setAnalysisCompletedClient(null);
    setAnalysisCompletedMonth(null);
  };

  const handleAnalysisStart = () => {
    setIsAnalysisInProgress(true);
  };

  const handleAnalysisComplete = (clientId: string, mesAnalise: string) => {
    setIsAnalysisInProgress(false);
    toast.update('analysis-progress', {
      render: (
        <div>
          Análise concluída com sucesso!
          <br />
          <button
            className="btn btn-sm btn-light mt-2"
            onClick={() => handleShowReportViewerModal(clientId, mesAnalise)}
          >
            Ver Relatório
          </button>
        </div>
      ),
      type: 'success',
      autoClose: 5000,
    });
    handleCloseAnalysisModal();
  };

  const handleAnalysisError = () => {
    setIsAnalysisInProgress(false);
  };

  if (loading) {
    return <div className="container mt-5">Carregando clientes...</div>;
  }

  if (error) {
    return <div className="container mt-5 text-danger">{error}</div>;
  }

  return (
    <div className="container mt-5">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="mb-0">Clientes</h1>
        <div>
          <button
            className="btn btn-info me-2"
            style={{ backgroundColor: 'var(--info-blue)', borderColor: 'var(--info-blue)', color: 'var(--primary-text)' }}
            onClick={() => handleShowReportViewerModal()}
          >
            Ver Relatórios
          </button>
          <button
            className="btn btn-success"
            style={{ backgroundColor: 'var(--info-blue)', borderColor: 'var(--info-blue)', color: 'var(--primary-text)' }}
            onClick={handleShowAddClientModal}
            disabled={isAnalysisInProgress} // Desabilita se a análise estiver em andamento
          >
            Adicionar Novo Cliente
          </button>
        </div>
      </div>

      {
        clients.length === 0 ? (
          <p>Nenhum cliente cadastrado. Adicione um novo cliente para começar.</p>
        ) : (
          <ul className="list-group">
            {clients.map((client) => (
              <li key={client.id} className="list-group-item d-flex justify-content-between align-items-center bg-dark text-white border-secondary mb-2">
                <div>
                  <h5>{client.nome_exibicao}</h5>
                  <small className="text-muted">ID: {client.id}</small>
                </div>
                <div>
                  <button
                    className="btn btn-warning me-2"
                    style={{ backgroundColor: 'var(--cta-yellow)', borderColor: 'var(--cta-yellow)', color: 'var(--dark-contrast)' }}
                    onClick={() => handleShowAnalysisModal(client)}
                    disabled={isAnalysisInProgress} // Desabilita se a análise estiver em andamento
                  >
                    Analisar
                  </button>
                  <button
                    className="btn btn-info me-2"
                    style={{ backgroundColor: 'var(--info-blue)', borderColor: 'var(--info-blue)', color: 'var(--primary-text)' }}
                    onClick={() => handleShowEditClientModal(client)}
                    disabled={isAnalysisInProgress} // Desabilita se a análise estiver em andamento
                  >
                    Editar
                  </button>
                  <button
                    className="btn btn-danger"
                    onClick={() => handleShowDeleteClientModal(client)}
                    disabled={isAnalysisInProgress} // Desabilita se a análise estiver em andamento
                  >
                    Excluir
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )
      }

      {selectedClient && (
        <AnalysisModal
          show={showAnalysisModal}
          handleClose={handleCloseAnalysisModal}
          client={selectedClient}
          onAnalysisStart={handleAnalysisStart} // Nova prop
          onAnalysisComplete={handleAnalysisComplete}
          onAnalysisError={handleAnalysisError} // Nova prop
        />
      )}

      <AddClientModal
        show={showAddClientModal}
        handleClose={handleCloseAddClientModal}
        onClientAdded={fetchClients}
      />

      {selectedClient && (
        <EditClientModal
          show={showEditClientModal}
          handleClose={handleCloseEditClientModal}
          client={selectedClient}
          onClientUpdated={fetchClients}
        />
      )}

      {selectedClient && (
        <DeleteClientModal
          show={showDeleteClientModal}
          handleClose={handleCloseDeleteClientModal}
          client={selectedClient}
          onClientDeleted={fetchClients}
        />
      )}

      <ReportViewerModal
        show={showReportViewerModal}
        handleClose={handleCloseReportViewerModal}
        clients={clients}
        initialClientId={analysisCompletedClient || undefined}
        initialMesAnalise={analysisCompletedMonth || undefined}
      />
    </div>
  );
};

export default HomePage;
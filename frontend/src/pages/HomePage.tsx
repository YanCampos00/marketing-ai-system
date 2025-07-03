import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import * as Types from '../types';
import AnalysisModal from '../components/AnalysisModal';
import AddClientModal from '../components/AddClientModal';
import EditClientModal from '../components/EditClientModal';
import DeleteClientModal from '../components/DeleteClientModal';
import { toast } from 'react-toastify';
import { useClient } from '../context/ClientContext'; // Importa o hook useClient

const HomePage: React.FC = () => {
  const { clients, loading, error } = useClient(); // Usa o contexto
  const [isAnalysisInProgress, setIsAnalysisInProgress] = useState<boolean>(false);

  // Estados para os modais
  const [showAnalysisModal, setShowAnalysisModal] = useState<boolean>(false);
  const [showAddClientModal, setShowAddClientModal] = useState<boolean>(false);
  const [showEditClientModal, setShowEditClientModal] = useState<boolean>(false);
  const [showDeleteClientModal, setShowDeleteClientModal] = useState<boolean>(false);
  const [selectedClient, setSelectedClient] = useState<Types.Client | null>(null);
  
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
    // fetchClients() é chamado automaticamente pelo ClientProvider após a adição
  };

  const handleShowEditClientModal = (client: Types.Client) => {
    setSelectedClient(client);
    setShowEditClientModal(true);
  };
  const handleCloseEditClientModal = () => {
    setShowEditClientModal(false);
    setSelectedClient(null);
    // fetchClients() é chamado automaticamente pelo ClientProvider após a edição
  };

  const handleShowDeleteClientModal = (client: Types.Client) => {
    setSelectedClient(client);
    setShowDeleteClientModal(true);
  };
  const handleCloseDeleteClientModal = () => {
    setShowDeleteClientModal(false);
    setSelectedClient(null);
    // fetchClients() é chamado automaticamente pelo ClientProvider após a exclusão
  };

  const handleAnalysisStart = () => {
    setIsAnalysisInProgress(true);
  };

  const handleAnalysisComplete = () => {
    setIsAnalysisInProgress(false);
    toast.update('analysis-progress', {
      render: (
        <div>
          Análise concluída com sucesso!
          <br />
          <Link to="/history" className="btn btn-sm btn-light mt-2">
            Ver no Histórico
          </Link>
        </div>
      ),
      type: 'success',
      autoClose: 5000,
      closeButton: true,
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
          <Link 
            to="/history"
            className="btn btn-cta me-2"
          >
            Ver Histórico
          </Link>
          <Link 
            to="/prompts"
            className="btn btn-cta me-2"
          >
            Gerenciar Prompts
          </Link>
          <button
            className="btn btn-cta"
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
                  <small className="text-white-50">ID: {client.id}</small>
                </div>
                <div>
                  <button
                    className="btn btn-cta me-2"
                    onClick={() => handleShowAnalysisModal(client)}
                    disabled={isAnalysisInProgress} // Desabilita se a análise estiver em andamento
                  >
                    Analisar
                  </button>
                  <button
                    className="btn btn-info-custom me-2"
                    onClick={() => handleShowEditClientModal(client)}
                    disabled={isAnalysisInProgress} // Desabilita se a análise estiver em andamento
                  >
                    Editar
                  </button>
                  <button
                    className="btn btn-danger-custom"
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
          onAnalysisStart={handleAnalysisStart}
          onAnalysisComplete={handleAnalysisComplete}
          onAnalysisError={handleAnalysisError}
        />
      )}

      <AddClientModal
        show={showAddClientModal}
        handleClose={handleCloseAddClientModal}
        
      />

      {selectedClient && (
        <EditClientModal
          show={showEditClientModal}
          handleClose={handleCloseEditClientModal}
          client={selectedClient}
          
        />
      )}

      {selectedClient && (
        <DeleteClientModal
          show={showDeleteClientModal}
          handleClose={handleCloseDeleteClientModal}
          client={selectedClient}
          
        />
      )}
    </div>
  );
};

export default HomePage;

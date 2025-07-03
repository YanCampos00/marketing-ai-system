import React, { useState } from 'react';
import { Modal, Button } from 'react-bootstrap';
import * as Types from '../types';
import { toast } from 'react-toastify';
import { useClient } from '../context/ClientContext'; // Importa o hook useClient

interface DeleteClientModalProps {
  show: boolean;
  handleClose: () => void;
  client: Types.Client | null;
  // onClientDeleted: () => void; // Removido, pois o contexto cuida da atualização
}

const DeleteClientModal: React.FC<DeleteClientModalProps> = ({ show, handleClose, client }) => {
  const { deleteClient } = useClient(); // Obtém a função deleteClient do contexto
  const [loading, setLoading] = useState<boolean>(false);

  const handleDelete = async () => {
    if (!client) return;

    setLoading(true);
    try {
      // Chama a função deleteClient do contexto
      await deleteClient(client.id);
      handleClose();
    } catch (error: any) {
      // Erro já tratado no contexto, mas pode-se adicionar lógica extra aqui se necessário
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal show={show} onHide={handleClose} centered>
      <Modal.Header closeButton className="bg-dark text-white">
        <Modal.Title>Confirmar Exclusão</Modal.Title>
      </Modal.Header>
      <Modal.Body className="bg-secondary text-white">
        <p>Tem certeza que deseja excluir o cliente <strong>{client?.nome_exibicao}</strong> (ID: {client?.id})?</p>
        <p className="text-danger">Esta ação é irreversível.</p>
      </Modal.Body>
      <Modal.Footer className="bg-dark">
        <Button variant="secondary" onClick={handleClose} disabled={loading}>
          Cancelar
        </Button>
        <Button className="btn-danger-custom" onClick={handleDelete} disabled={loading}>
          {loading ? 'Excluindo...' : 'Excluir'}
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default DeleteClientModal;
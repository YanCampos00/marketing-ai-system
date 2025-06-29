import React, { useState } from 'react';
import { Modal, Button } from 'react-bootstrap';
import api from '../services/api';
import * as Types from '../types'; // Importa tudo como Types
import { toast } from 'react-toastify';

interface DeleteClientModalProps {
  show: boolean;
  handleClose: () => void;
  client: Types.Client | null;
  onClientDeleted: () => void; // Callback para atualizar a lista de clientes
}

const DeleteClientModal: React.FC<DeleteClientModalProps> = ({ show, handleClose, client, onClientDeleted }) => {
  const [loading, setLoading] = useState<boolean>(false);

  const handleDelete = async () => {
    if (!client) return;

    setLoading(true);
    try {
      await api.delete(`/clients/${client.id}`);
      toast.success('Cliente excluído com sucesso!');
      onClientDeleted();
      handleClose();
    } catch (error: any) {
      console.error('Erro ao excluir cliente:', error);
      toast.error(`Erro ao excluir cliente: ${error.response?.data?.detail || error.message}`);
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
        <Button variant="danger" onClick={handleDelete} disabled={loading}>
          {loading ? 'Excluindo...' : 'Excluir'}
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default DeleteClientModal;
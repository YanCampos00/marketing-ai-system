import React, { useState } from 'react';
import { Modal, Button, Form } from 'react-bootstrap';
import api from '../services/api';
import * as Types from '../types'; // Importa tudo como Types
import { toast } from 'react-toastify';

interface AddClientModalProps {
  show: boolean;
  handleClose: () => void;
  onClientAdded: () => void; // Callback para atualizar a lista de clientes
}

const AddClientModal: React.FC<AddClientModalProps> = ({ show, handleClose, onClientAdded }) => {
  const [clientData, setClientData] = useState<Partial<Types.Client>>({
    id: '',
    nome_exibicao: '',
    contexto_cliente_prompt: '',
    planilha_id_ou_nome: '',
    google_sheet_tab_name: '',
    meta_sheet_tab_name: '',
  });
  const [loading, setLoading] = useState<boolean>(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { id, value } = e.target;
    setClientData(prev => ({ ...prev, [id]: value }));
  };

  const handleSubmit = async () => {
    if (!clientData.id || !clientData.nome_exibicao || !clientData.contexto_cliente_prompt || !clientData.planilha_id_ou_nome) {
      toast.error('Por favor, preencha todos os campos obrigatórios (ID, Nome, Contexto, Planilha).');
      return;
    }

    setLoading(true);
    try {
      await api.post('/clients', clientData);
      toast.success('Cliente adicionado com sucesso!');
      onClientAdded();
      handleClose();
    } catch (error: any) {
      console.error('Erro ao adicionar cliente:', error);
      toast.error(`Erro ao adicionar cliente: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal show={show} onHide={handleClose} centered size="lg">
      <Modal.Header closeButton className="bg-dark text-white">
        <Modal.Title>Adicionar Novo Cliente</Modal.Title>
      </Modal.Header>
      <Modal.Body className="bg-secondary text-white">
        <Form>
          <Form.Group className="mb-3" controlId="id">
            <Form.Label>ID do Cliente (Único)</Form.Label>
            <Form.Control type="text" value={clientData.id} onChange={handleChange} className="bg-dark text-white border-secondary" />
          </Form.Group>
          <Form.Group className="mb-3" controlId="nome_exibicao">
            <Form.Label>Nome de Exibição</Form.Label>
            <Form.Control type="text" value={clientData.nome_exibicao} onChange={handleChange} className="bg-dark text-white border-secondary" />
          </Form.Group>
          <Form.Group className="mb-3" controlId="contexto_cliente_prompt">
            <Form.Label>Contexto do Cliente (Prompt para IA)</Form.Label>
            <Form.Control as="textarea" rows={3} value={clientData.contexto_cliente_prompt} onChange={handleChange} className="bg-dark text-white border-secondary" />
          </Form.Group>
          <Form.Group className="mb-3" controlId="planilha_id_ou_nome">
            <Form.Label>ID/Nome da Planilha Google Sheets</Form.Label>
            <Form.Control type="text" value={clientData.planilha_id_ou_nome} onChange={handleChange} className="bg-dark text-white border-secondary" />
          </Form.Group>
          <Form.Group className="mb-3" controlId="google_sheet_tab_name">
            <Form.Label>Nome da Aba Google Ads (Opcional)</Form.Label>
            <Form.Control type="text" value={clientData.google_sheet_tab_name} onChange={handleChange} className="bg-dark text-white border-secondary" placeholder="Deixe em branco para padrão" />
          </Form.Group>
          <Form.Group className="mb-3" controlId="meta_sheet_tab_name">
            <Form.Label>Nome da Aba Meta Ads (Opcional)</Form.Label>
            <Form.Control type="text" value={clientData.meta_sheet_tab_name} onChange={handleChange} className="bg-dark text-white border-secondary" placeholder="Deixe em branco para padrão" />
          </Form.Group>
        </Form>
      </Modal.Body>
      <Modal.Footer className="bg-dark">
        <Button variant="secondary" onClick={handleClose} disabled={loading}>
          Cancelar
        </Button>
        <Button
          style={{ backgroundColor: 'var(--cta-yellow)', borderColor: 'var(--cta-yellow)', color: 'var(--dark-contrast)' }}
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? 'Adicionando...' : 'Adicionar Cliente'}
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default AddClientModal;
import React, { useEffect, useState } from 'react';
import { Container, Row, Col, Card, Button, Spinner, Alert, Modal, Form } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import api from '../services/api';
import * as Types from '../types';
import { toast } from 'react-toastify';

interface Prompt {
  id: string;
  nome: string;
  conteudo: string;
  descricao?: string;
}

const PromptManagementPage: React.FC = () => {
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showEditModal, setShowEditModal] = useState<boolean>(false);
  const [selectedPrompt, setSelectedPrompt] = useState<Prompt | null>(null);
  const [editedContent, setEditedContent] = useState<string>('');
  const [editedDescription, setEditedDescription] = useState<string>('');

  const fetchPrompts = async () => {
    try {
      setLoading(true);
      const response = await api.get<Prompt[]>('/prompts');
      setPrompts(response.data);
    } catch (err) {
      setError('Erro ao carregar prompts.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPrompts();
  }, []);

  const handleEditClick = (prompt: Prompt) => {
    setSelectedPrompt(prompt);
    setEditedContent(prompt.conteudo);
    setEditedDescription(prompt.descricao || '');
    setShowEditModal(true);
  };

  const handleCloseEditModal = () => {
    setShowEditModal(false);
    setSelectedPrompt(null);
    setEditedContent('');
    setEditedDescription('');
  };

  const handleSavePrompt = async () => {
    if (!selectedPrompt) return;

    try {
      await api.put(`/prompts/${selectedPrompt.nome}`, {
        nome: selectedPrompt.nome,
        conteudo: editedContent,
        descricao: editedDescription,
      });
      toast.success('Prompt atualizado com sucesso!');
      fetchPrompts(); // Recarregar prompts após a atualização
      handleCloseEditModal();
    } catch (err: any) {
      toast.error(`Erro ao atualizar prompt: ${err.response?.data?.detail || err.message}`);
      console.error(err);
    }
  };

  if (loading) {
    return <Container className="mt-5 text-center"><Spinner animation="border" /></Container>;
  }

  if (error) {
    return <Container className="mt-5"><Alert variant="danger">{error}</Alert></Container>;
  }

  return (
    <Container className="mt-5">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="mb-0 text-white">Gerenciamento de Prompts</h1>
        <Link to="/" className="btn btn-warning" style={{ backgroundColor: 'var(--cta-yellow)', borderColor: 'var(--cta-yellow)', color: 'var(--dark-contrast)' }}>Voltar para Home</Link>
      </div>
      <Row>
        {prompts.length === 0 ? (
          <Col><Alert variant="info">Nenhum prompt encontrado.</Alert></Col>
        ) : (
          prompts.map((prompt) => (
            <Col md={6} lg={4} key={prompt.id} className="mb-4">
              <Card className="bg-dark text-white h-100">
                <Card.Body>
                  <Card.Title>{prompt.nome}</Card.Title>
                  <Card.Subtitle className="mb-2 text-white-50">ID: {prompt.id}</Card.Subtitle>
                  <Card.Text className="text-white-50">
                    {prompt.descricao || 'Sem descrição.'}
                  </Card.Text>
                  <Button 
                    variant="primary" 
                    style={{ backgroundColor: 'var(--cta-yellow)', borderColor: 'var(--cta-yellow)', color: 'var(--dark-contrast)' }}
                    onClick={() => handleEditClick(prompt)}
                  >
                    Editar
                  </Button>
                </Card.Body>
              </Card>
            </Col>
          ))
        )}
      </Row>

      {/* Modal de Edição */}
      <Modal show={showEditModal} onHide={handleCloseEditModal} size="lg" centered>
        <Modal.Header closeButton className="bg-dark text-white">
          <Modal.Title>Editar Prompt: {selectedPrompt?.nome}</Modal.Title>
        </Modal.Header>
        <Modal.Body className="bg-secondary text-white">
          <Form>
            <Form.Group className="mb-3" controlId="promptContent">
              <Form.Label>Conteúdo do Prompt</Form.Label>
              <Form.Control
                as="textarea"
                rows={15}
                value={editedContent}
                onChange={(e) => setEditedContent(e.target.value)}
                className="bg-dark text-white border-secondary"
              />
            </Form.Group>
            <Form.Group className="mb-3" controlId="promptDescription">
              <Form.Label>Descrição</Form.Label>
              <Form.Control
                type="text"
                value={editedDescription}
                onChange={(e) => setEditedDescription(e.target.value)}
                className="bg-dark text-white border-secondary"
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer className="bg-dark">
          <Button variant="secondary" onClick={handleCloseEditModal}>
            Cancelar
          </Button>
          <Button 
            variant="primary" 
            style={{ backgroundColor: 'var(--cta-yellow)', borderColor: 'var(--cta-yellow)', color: 'var(--dark-contrast)' }}
            onClick={handleSavePrompt}
          >
            Salvar Alterações
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default PromptManagementPage;

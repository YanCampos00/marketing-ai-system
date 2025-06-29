
import React, { useState, useEffect } from 'react';
import { Modal, Button, Form } from 'react-bootstrap';
import Select from 'react-select';
import * as Types from '../types';
import api from '../services/api';
import { toast } from 'react-toastify';

interface AnalysisModalProps {
  show: boolean;
  handleClose: () => void;
  client: Types.Client | null;
  onAnalysisStart: () => void; // Nova prop
  onAnalysisComplete: (clientId: string, mesAnalise: string) => void;
  onAnalysisError: () => void; // Nova prop
}

const AnalysisModal: React.FC<AnalysisModalProps> = ({ show, handleClose, client, onAnalysisStart, onAnalysisComplete, onAnalysisError }) => {
  const [mesAnalise, setMesAnalise] = useState<string>('');
  const [metricasSelecionadas, setMetricasSelecionadas] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [availableMetrics, setAvailableMetrics] = useState<{ value: string; label: string }[]>([]);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await api.get<string[]>('/metrics');
        const formattedMetrics = response.data.map(metric => ({
          value: metric.toLowerCase(), // Garante que o valor seja em minúsculas
          label: metric.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()), // Formata para exibição
        }));
        setAvailableMetrics(formattedMetrics);
      } catch (error) {
        console.error('Erro ao carregar métricas disponíveis:', error);
        toast.error('Erro ao carregar métricas disponíveis.');
      }
    };

    if (show) {
      fetchMetrics();
    }
  }, [show]);

  const handleSubmit = async () => {
    if (!client || !mesAnalise) {
      toast.error('Por favor, selecione o mês de análise.');
      return;
    }

    setLoading(true);
    onAnalysisStart(); // Notifica o início da análise
    toast.info('Análise em andamento...', { toastId: 'analysis-progress', autoClose: false, closeButton: false });

    const requestData: Types.AnalysisRequest = {
      client_id: client.id,
      mes_analise: mesAnalise,
      metricas_selecionadas: metricasSelecionadas.map(m => m.value),
    };

    try {
      await api.post('/analyze', requestData);
      console.log('Análise concluída no backend, chamando onAnalysisComplete.');
      onAnalysisComplete(client.id, mesAnalise); // Chama o callback de sucesso
    } catch (error: any) {
      console.error('Erro ao iniciar análise:', error);
      toast.update('analysis-progress', { render: `Erro ao iniciar análise: ${error.response?.data?.detail || error.message}`, type: 'error', autoClose: 5000 });
      onAnalysisError(); // Notifica o erro na análise
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal show={show} onHide={handleClose} centered>
      <Modal.Header closeButton className="bg-dark text-white">
        <Modal.Title>Analisar {client?.nome_exibicao}</Modal.Title>
      </Modal.Header>
      <Modal.Body className="bg-secondary text-white">
        <Form>
          <Form.Group className="mb-3" controlId="formMesAnalise">
            <Form.Label>Mês de Análise</Form.Label>
            <Form.Control
              type="date"
              value={mesAnalise}
              onChange={(e) => setMesAnalise(e.target.value)}
              className="bg-dark text-white border-secondary"
            />
          </Form.Group>

          <Form.Group className="mb-3" controlId="formMetricas">
            <Form.Label>Métricas Selecionadas</Form.Label>
            <Select
              isMulti
              name="metricas"
              options={availableMetrics}
              className="basic-multi-select"
              classNamePrefix="select"
              onChange={(selectedOptions) => setMetricasSelecionadas(selectedOptions as any[])}
              value={metricasSelecionadas}
              placeholder="Selecione as métricas..."
              styles={{
                control: (base) => ({
                  ...base,
                  backgroundColor: 'var(--secondary-bg)',
                  borderColor: 'var(--secondary-bg)',
                  color: 'var(--primary-text)',
                }),
                menu: (base) => ({
                  ...base,
                  backgroundColor: 'var(--secondary-bg)',
                }),
                option: (base, state) => ({
                  ...base,
                  backgroundColor: state.isFocused ? 'var(--cta-yellow)' : 'var(--secondary-bg)',
                  color: state.isFocused ? 'var(--dark-contrast)' : 'var(--primary-text)',
                }),
                multiValue: (base) => ({
                  ...base,
                  backgroundColor: 'var(--cta-yellow)',
                  color: 'var(--dark-contrast)',
                }),
                multiValueLabel: (base) => ({
                  ...base,
                  color: 'var(--dark-contrast)',
                }),
                singleValue: (base) => ({
                  ...base,
                  color: 'var(--primary-text)',
                }),
                input: (base) => ({
                  ...base,
                  color: 'var(--primary-text)',
                }),
              }}
            />
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
          {loading ? 'Analisando...' : 'Iniciar Análise'}
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default AnalysisModal;

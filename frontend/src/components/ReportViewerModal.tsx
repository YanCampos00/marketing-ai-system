import React, { useState, useEffect, useCallback } from 'react';
import { Modal, Button, Form, ListGroup } from 'react-bootstrap';
import api from '../services/api';
import { toast } from 'react-toastify';
import * as Types from '../types';

interface ReportViewerModalProps {
  show: boolean;
  handleClose: () => void;
  clients: Types.Client[]; // Lista de clientes para seleção de filtro
  initialClientId?: string; // Cliente pré-selecionado (para quando vem da notificação)
  initialMesAnalise?: string; // Mês pré-selecionado (para quando vem da notificação)
}

interface ReportSummary {
  client_id: string;
  client_name: string;
  mes_analise: string;
  file_name: string;
  file_path: string;
}

const ReportViewerModal: React.FC<ReportViewerModalProps> = ({ show, handleClose, clients, initialClientId, initialMesAnalise }) => {
  const [allReports, setAllReports] = useState<ReportSummary[]>([]);
  const [filteredReports, setFilteredReports] = useState<ReportSummary[]>([]);
  const [selectedReportContent, setSelectedReportContent] = useState<string | null>(null);
  const [loadingReports, setLoadingReports] = useState<boolean>(false);
  const [loadingReportContent, setLoadingReportContent] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const [filterClient, setFilterClient] = useState<string>(initialClientId || '');
  const [filterMonth, setFilterMonth] = useState<string>(initialMesAnalise || '');

  const fetchAllReports = useCallback(async () => {
    setLoadingReports(true);
    setError(null);
    try {
      const response = await api.get<ReportSummary[]>('/reports/list');
      setAllReports(response.data);
      setFilteredReports(response.data);
    } catch (err: any) {
      console.error('Erro ao listar relatórios:', err);
      setError(`Erro ao listar relatórios: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoadingReports(false);
    }
  }, []); // Dependências vazias, pois a função não depende de props ou estados que mudam

  useEffect(() => {
    if (show) {
      fetchAllReports();
      // Resetar filtros e conteúdo ao abrir o modal
      setFilterClient(initialClientId || '');
      setFilterMonth(initialMesAnalise || '');
      setSelectedReportContent(null);
    }
  }, [show, fetchAllReports, initialClientId, initialMesAnalise]);

  useEffect(() => {
    let tempReports = allReports;

    if (filterClient) {
      tempReports = tempReports.filter(report => report.client_id === filterClient);
    }

    if (filterMonth) {
      tempReports = tempReports.filter(report => report.mes_analise.startsWith(filterMonth));
    }

    setFilteredReports(tempReports);

    // Tenta carregar o relatório inicial após a filtragem
    if (show && initialClientId && initialMesAnalise && tempReports.length > 0) {
      const reportToLoad = tempReports.find(r => r.client_id === initialClientId && r.mes_analise === initialMesAnalise);
      if (reportToLoad && !selectedReportContent) { // Evita recarregar se já estiver carregado
        fetchReportContent(reportToLoad.client_id, reportToLoad.mes_analise);
      }
    }

  }, [filterClient, filterMonth, allReports, initialClientId, initialMesAnalise, show, selectedReportContent]);

  const fetchReportContent = async (clientId: string, mesAnalise: string) => {
    setLoadingReportContent(true);
    setError(null);
    try {
      const response = await api.get(`/reports/${clientId}/${mesAnalise}`);
      setSelectedReportContent(response.data.report_content);
    } catch (err: any) {
      console.error('Erro ao carregar conteúdo do relatório:', err);
      setError(`Erro ao carregar conteúdo do relatório: ${err.response?.data?.detail || err.message}`);
      setSelectedReportContent('Não foi possível carregar o conteúdo do relatório.');
    } finally {
      setLoadingReportContent(false);
    }
  };

  const handleClearFilters = () => {
    setFilterClient('');
    setFilterMonth('');
    setSelectedReportContent(null);
  };

  return (
    <Modal show={show} onHide={handleClose} centered size="xl">
      <Modal.Header closeButton className="bg-dark text-white">
        <Modal.Title>Visualizar Relatórios</Modal.Title>
      </Modal.Header>
      <Modal.Body className="bg-secondary text-white">
        <Form className="mb-3">
          <div className="row">
            <Form.Group className="col-md-6 mb-3" controlId="filterClient">
              <Form.Label>Filtrar por Cliente</Form.Label>
              <Form.Control
                as="select"
                value={filterClient}
                onChange={(e) => setFilterClient(e.target.value)}
                className="bg-dark text-white border-secondary"
              >
                <option value="">Todos os Clientes</option>
                {clients.map((client) => (
                  <option key={client.id} value={client.id}>
                    {client.nome_exibicao}
                  </option>
                ))}
              </Form.Control>
            </Form.Group>

            <Form.Group className="col-md-6 mb-3" controlId="filterMonth">
              <Form.Label>Filtrar por Mês</Form.Label>
              <Form.Control
                type="month"
                value={filterMonth}
                onChange={(e) => setFilterMonth(e.target.value)}
                className="bg-dark text-white border-secondary"
              />
            </Form.Group>
          </div>
          <Button variant="secondary" onClick={handleClearFilters}>Limpar Filtros</Button>
        </Form>

        {loadingReports ? (
          <div>Carregando relatórios...</div>
        ) : error ? (
          <div className="alert alert-danger">{error}</div>
        ) : filteredReports.length === 0 ? (
          <p>Nenhum relatório encontrado com os filtros aplicados.</p>
        ) : (
          <div className="row">
            <div className="col-md-4">
              <ListGroup className="report-list" style={{ maxHeight: '60vh', overflowY: 'auto' }}>
                {filteredReports.map((report, index) => (
                  <ListGroup.Item
                    key={index}
                    action
                    onClick={() => fetchReportContent(report.client_id, report.mes_analise)}
                    className="bg-dark text-white border-secondary mb-1"
                  >
                    <strong>{report.client_name}</strong> - {report.mes_analise}
                  </ListGroup.Item>
                ))}
              </ListGroup>
            </div>
            <div className="col-md-8">
              {loadingReportContent ? (
                <div>Carregando conteúdo do relatório...</div>
              ) : selectedReportContent ? (
                <div className="p-3 border rounded bg-dark text-white" style={{ maxHeight: '60vh', overflowY: 'auto' }}>
                  <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>{selectedReportContent}</pre>
                </div>
              ) : (
                <p>Selecione um relatório na lista para visualizar o conteúdo.</p>
              )}
            </div>
          </div>
        )}
      </Modal.Body>
      <Modal.Footer className="bg-dark">
        <Button variant="secondary" onClick={handleClose}>
          Fechar
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default ReportViewerModal;
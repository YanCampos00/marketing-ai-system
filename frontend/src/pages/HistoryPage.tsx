import React, { useEffect, useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { Container, Card, Button, Row, Col, Spinner, Alert, Form } from 'react-bootstrap';
import api from '../services/api';
import * as Types from '../types';
import ReportViewerModal from '../components/ReportViewerModal'; // Importe o novo modal

const HistoryPage: React.FC = () => {
  const [reports, setReports] = useState<Types.ReportSummary[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [clients, setClients] = useState<Types.Client[]>([]);

  // Estados dos filtros
  const [selectedClient, setSelectedClient] = useState<string>('');
  const [selectedDate, setSelectedDate] = useState<string>('');

  // Estados para o modal de visualização
  const [showReportModal, setShowReportModal] = useState<boolean>(false);
  const [selectedReportContent, setSelectedReportContent] = useState<string>('');
  const [selectedReportTitle, setSelectedReportTitle] = useState<string>('');

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const [reportsResponse, clientsResponse] = await Promise.all([
          api.get<Types.ReportSummary[]>('/reports/list'),
          api.get<{ [key: string]: Types.Client }>('/clients'),
        ]);

        const sortedReports = reportsResponse.data.sort((a, b) => 
            new Date(b.mes_analise).getTime() - new Date(a.mes_analise).getTime()
        );
        setReports(sortedReports);
        setClients(Object.values(clientsResponse.data));

      } catch (err) {
        setError('Erro ao carregar dados.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchInitialData();
  }, []);

  const handleShowReportModal = async (report: Types.ReportSummary) => {
    setSelectedReportTitle(`Relatório - ${report.client_name} - ${new Date(report.mes_analise).toLocaleDateString('pt-BR', { month: 'long', year: 'numeric', timeZone: 'UTC' })}`);
    try {
      const response = await api.get<Types.ReportContent>(`/reports/view/${report.file_name}`);
      console.log("API Response:", response);
      setSelectedReportContent(response.data.report_content);
      setShowReportModal(true);
    } catch (error) {
      console.error('Erro ao carregar o conteúdo do relatório:', error);
      setError('Não foi possível carregar o relatório.');
    }
  };

  const handleCloseReportModal = () => {
    setShowReportModal(false);
    setSelectedReportContent('');
    setSelectedReportTitle('');
  };

  const filteredReports = useMemo(() => {
    return reports.filter(report => {
      const clientMatch = selectedClient ? report.client_id === selectedClient : true;
      const dateMatch = selectedDate ? report.mes_analise.startsWith(selectedDate) : true;
      return clientMatch && dateMatch;
    });
  }, [reports, selectedClient, selectedDate]);

  const uniqueDates = useMemo(() => {
    const dates = new Set(reports.map(r => r.mes_analise.substring(0, 7))); // Pega 'YYYY-MM'
    return Array.from(dates).map(date => {
        const [year, month] = date.split('-');
        return {
            value: date,
            label: new Date(parseInt(year), parseInt(month) - 1).toLocaleDateString('pt-BR', { month: 'long', year: 'numeric', timeZone: 'UTC' })
        };
    });
}, [reports]);


  return (
    <Container className="mt-5">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="mb-0">Histórico de Análises</h1>
        <Link to="/" className="btn btn-warning" style={{ backgroundColor: 'var(--cta-yellow)', borderColor: 'var(--cta-yellow)', color: 'var(--dark-contrast)' }}>Voltar para Home</Link>
      </div>

      {/* Filtros */}
      <Row className="mb-4">
        <Col md={6}>
          <Form.Group controlId="filterClient">
            <Form.Label className='text-white'>Filtrar por Cliente</Form.Label>
            <Form.Select 
              value={selectedClient}
              onChange={(e) => setSelectedClient(e.target.value)}
              className="bg-dark text-white border-secondary"
            >
              <option value="">Todos os Clientes</option>
              {clients.map(client => (
                <option key={client.id} value={client.id}>{client.nome_exibicao}</option>
              ))}
            </Form.Select>
          </Form.Group>
        </Col>
        <Col md={6}>
          <Form.Group controlId="filterDate">
            <Form.Label className='text-white'>Filtrar por Mês</Form.Label>
            <Form.Select 
              value={selectedDate} 
              onChange={(e) => setSelectedDate(e.target.value)}
              className="bg-dark text-white border-secondary"
            >
              <option value="">Todos os Meses</option>
              {uniqueDates.map(date => (
                <option key={date.value} value={date.value}>{date.label}</option>
              ))}
            </Form.Select>
          </Form.Group>
        </Col>
      </Row>

      {loading && (
        <div className="text-center">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Carregando...</span>
          </Spinner>
        </div>
      )}

      {error && <Alert variant="danger">{error}</Alert>}

      {!loading && !error && (
        <Row>
          {filteredReports.length > 0 ? (
            filteredReports.map((report, index) => (
              <Col md={6} lg={4} key={index} className="mb-4">
                <Card className="bg-dark text-white h-100">
                  <Card.Body>
                    <Card.Title>{report.client_name}</Card.Title>
                    <Card.Subtitle className="mb-2">
                      <span className="text-white-50">Análise de: {new Date(report.mes_analise).toLocaleDateString('pt-BR', { month: 'long', year: 'numeric', timeZone: 'UTC' })}</span>
                    </Card.Subtitle>
                    <Card.Text>
                      <small>ID do Cliente: {report.client_id}</small>
                    </Card.Text>
                    <Button 
                      variant="primary" 
                      style={{ backgroundColor: 'var(--cta-yellow)', borderColor: 'var(--cta-yellow)', color: 'var(--dark-contrast)' }}
                      onClick={() => handleShowReportModal(report)}
                    >
                      Ver Relatório Detalhado
                    </Button>
                  </Card.Body>
                </Card>
              </Col>
            ))
          ) : (
            <Col>
              <Alert variant="info">Nenhum relatório encontrado para os filtros selecionados.</Alert>
            </Col>
          )}
        </Row>
      )}
      
      <ReportViewerModal
        show={showReportModal}
        handleClose={handleCloseReportModal}
        title={selectedReportTitle}
        reportContent={selectedReportContent}
      />

    </Container>
  );
};

export default HistoryPage;

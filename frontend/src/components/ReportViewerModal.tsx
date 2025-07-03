import React from 'react';
import { Modal, Button } from 'react-bootstrap';

interface ReportViewerModalProps {
  show: boolean;
  handleClose: () => void;
  title: string;
  reportContent: string;
}

const ReportViewerModal: React.FC<ReportViewerModalProps> = ({ show, handleClose, title, reportContent }) => {
  return (
    <Modal show={show} onHide={handleClose} size="lg" centered>
      <Modal.Header closeButton className="bg-dark text-white">
        <Modal.Title>{title}</Modal.Title>
      </Modal.Header>
      <Modal.Body className="bg-secondary text-white" style={{ whiteSpace: 'pre-wrap' }}>
        {reportContent}
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

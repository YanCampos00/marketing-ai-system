
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import HistoryPage from './pages/HistoryPage';
import PromptManagementPage from './pages/PromptManagementPage';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { ClientProvider } from './context/ClientContext';
import { PromptProvider } from './context/PromptContext'; // Importa o PromptProvider

function App() {
  return (
    <ClientProvider> {/* Envolve toda a aplicação com ClientProvider */}
      <PromptProvider> {/* Envolve a aplicação com PromptProvider também */}
        <Router>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/prompts" element={<PromptManagementPage />} />
          </Routes>
          <ToastContainer
            position="bottom-right"
            autoClose={5000}
            hideProgressBar={false}
            newestOnTop={false}
            closeOnClick
            rtl={false}
            pauseOnFocusLoss
            draggable
            pauseOnHover
          />
        </Router>
      </PromptProvider>
    </ClientProvider>
  );
}

export default App;

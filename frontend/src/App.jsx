import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useState } from 'react';
import Navbar from './components/Navbar';
import UploadPage from './pages/UploadPage';
import OverviewPage from './pages/OverviewPage';
import RankingPage from './pages/RankingPage';
import DrilldownPage from './pages/DrilldownPage';
import NegativeSpacePage from './pages/NegativeSpacePage';

export default function App() {
  const [batchId, setBatchId] = useState(null);
  
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-900">
        <Navbar batchId={batchId} />
        <Routes>
          <Route path="/" element={<UploadPage onBatchReady={setBatchId} />} />
          <Route path="/overview" element={batchId ? <OverviewPage batchId={batchId} /> : <Navigate to="/" />} />
          <Route path="/ranking" element={batchId ? <RankingPage batchId={batchId} /> : <Navigate to="/" />} />
          <Route path="/entity/:cseId" element={batchId ? <DrilldownPage batchId={batchId} /> : <Navigate to="/" />} />
          <Route path="/negative-space" element={batchId ? <NegativeSpacePage batchId={batchId} /> : <Navigate to="/" />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

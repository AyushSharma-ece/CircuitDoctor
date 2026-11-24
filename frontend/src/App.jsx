import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import NewInspection from './pages/NewInspection';
import InspectionHistory from './pages/InspectionHistory';
import DefectAnalysis from './pages/DefectAnalysis';
import ModelInformation from './pages/ModelInformation';
import DatasetInformation from './pages/DatasetInformation';
import Settings from './pages/Settings';
import About from './pages/About';

import { getHealth, getModelInfo, getStatistics, getInspections } from './services/api';

export default function App() {
  const [health, setHealth] = useState(null);
  const [modelInfo, setModelInfo] = useState(null);
  const [stats, setStats] = useState(null);
  const [recentInspections, setRecentInspections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchGlobalData = async () => {
    setRefreshing(true);
    try {
      const [hData, mData, sData, iData] = await Promise.all([
        getHealth().catch(() => ({ status: 'offline', model_status: 'unreachable', device: 'unknown' })),
        getModelInfo().catch(() => null),
        getStatistics().catch(() => null),
        getInspections({ limit: 10 }).catch(() => [])
      ]);

      setHealth(hData);
      setModelInfo(mData);
      setStats(sData);
      setRecentInspections(iData || []);
    } catch (err) {
      console.error('[CircuitDoctor] Error fetching system data:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchGlobalData();
  }, []);

  return (
    <Router>
      <div className="flex h-screen bg-navy-950 text-slate-100 overflow-hidden font-sans">
        {/* Fixed Industrial Sidebar */}
        <Sidebar health={health} modelInfo={modelInfo} />

        {/* Scrollable Main Application Content Area */}
        <div className="flex-1 flex flex-col min-w-0 overflow-y-auto pcb-grid">
          <Header
            title="CircuitDoctor Industrial Inspection Suite"
            onRefresh={fetchGlobalData}
            isRefreshing={refreshing}
          />

          <main className="flex-1 pb-12">
            <Routes>
              <Route
                path="/"
                element={
                  <Dashboard
                    stats={stats}
                    health={health}
                    modelInfo={modelInfo}
                    recentInspections={recentInspections}
                    loading={loading}
                  />
                }
              />
              <Route
                path="/inspect"
                element={
                  <NewInspection
                    health={health}
                    onInspectionCompleted={fetchGlobalData}
                  />
                }
              />
              <Route path="/history" element={<InspectionHistory />} />
              <Route path="/analysis" element={<DefectAnalysis stats={stats} />} />
              <Route
                path="/model"
                element={<ModelInformation modelInfo={modelInfo} health={health} />}
              />
              <Route path="/dataset" element={<DatasetInformation />} />
              <Route
                path="/settings"
                element={<Settings health={health} modelInfo={modelInfo} />}
              />
              <Route path="/about" element={<About />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

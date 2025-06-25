// File: frontend/pages/index.jsx
'use client';

import { useEffect, useState } from 'react';
import Topologia from '../components/Topologia';
import Spinner from '../components/ui/Spinner';
import Alert from '../components/ui/Alert';

export default function HomePage() {
  const [data, setData] = useState({ nodes: [], edges: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTopology = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch('http://localhost:8000/api/monitoring/topology', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ip_list: ['45.172.141.122', '45.172.141.35'] }),
        });

        if (!res.ok) {
          throw new Error(`HTTP ${res.status} ${await res.text()}`);
        }

        const json = await res.json();
        setData({ nodes: json.nodes ?? [], edges: json.edges ?? [] });
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };

    fetchTopology();
  }, []);

  if (loading) {
    return (
      <div className="flex h-screen w-screen items-center justify-center">
        <Spinner> Cargando topología… </Spinner>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-screen w-screen items-center justify-center p-4">
        <Alert severity="error" title="Error al cargar">
          {error}
        </Alert>
      </div>
    );
  }

  return (
    <div className="h-screen w-screen overflow-hidden">
      <Topologia nodes={data.nodes} edges={data.edges} />
    </div>
  );
}

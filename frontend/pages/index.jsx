// File: frontend/pages/index.jsx
import { useEffect, useState } from 'react';
import Topologia from '../components/Topologia';

export default function HomePage() {
  const [data, setData] = useState({ nodes: [], edges: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch('http://localhost:8000/api/monitoring/topology', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ip_list: ['45.172.141.122', '45.172.141.35'] }),
        });
        if (!res.ok) {
          const errText = await res.text();
          throw new Error(`HTTP ${res.status}: ${errText}`);
        }
        const json = await res.json();
        setData({ nodes: json.nodes || [], edges: json.edges || [] });
      } catch (err) {
        console.error('Error al obtener topología', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center w-screen h-screen">
        <div className="text-xl">🔄 Cargando topología…</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center w-screen h-screen p-4">
        <div className="mb-4 text-red-600 font-semibold">Error al cargar la topología:</div>
        <pre className="bg-gray-100 p-4 rounded">{error}</pre>
      </div>
    );
  }

  return (
    <div className="w-screen h-screen overflow-hidden">
      <Topologia nodes={data.nodes} edges={data.edges} />
    </div>
  );
}

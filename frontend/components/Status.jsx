// File: frontend/components/Status.jsx

import React, { useEffect, useState } from 'react';
import Spinner from './ui/Spinner';
import Alert from './ui/Alert';

export default function Status({
  apiUrl = 'http://localhost:8000/api/monitoring/status',
}) {
  const [data, setData] = useState({ mikrotik: [], uisp: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchStatus() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(apiUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            ip_list: ['45.172.141.122', '45.172.141.35'],
          }),
        });
        if (!res.ok) {
          const txt = await res.text();
          throw new Error(`HTTP ${res.status}: ${txt}`);
        }
        const json = await res.json();
        setData({
          mikrotik: Array.isArray(json.mikrotik) ? json.mikrotik : [],
          uisp: Array.isArray(json.uisp) ? json.uisp : [],
        });
      } catch (err) {
        console.error('Error fetching status', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchStatus();
  }, [apiUrl]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Spinner size="xl" />
      </div>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        <strong>Error cargando estado:</strong>
        <pre>{error}</pre>
      </Alert>
    );
  }

  if (data.mikrotik.length === 0 && data.uisp.length === 0) {
    return (
      <Alert severity="warning">
        No se encontraron datos de estado.
      </Alert>
    );
  }

  return (
    <div className="p-4 space-y-6">
      <section>
        <h2 className="text-xl font-bold mb-2">MikroTik</h2>
        <table className="w-full table-auto border-collapse">
          <thead>
            <tr>
              <th className="border px-2 py-1">IP</th>
              <th className="border px-2 py-1">Online</th>
              <th className="border px-2 py-1">Latencia (ms)</th>
            </tr>
          </thead>
          <tbody>
            {data.mikrotik.map((r) => (
              <tr key={r.ip}>
                <td className="border px-2 py-1">{r.ip}</td>
                <td className="border px-2 py-1">
                  {r.online ? '✔️' : '❌'}
                </td>
                <td className="border px-2 py-1">
                  {r.latency ?? '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section>
        <h2 className="text-xl font-bold mb-2">UISP Devices</h2>
        <table className="w-full table-auto border-collapse">
          <thead>
            <tr>
              <th className="border px-2 py-1">ID</th>
              <th className="border px-2 py-1">Name</th>
              <th className="border px-2 py-1">IP</th>
              <th className="border px-2 py-1">MAC</th>
            </tr>
          </thead>
          <tbody>
            {data.uisp.map((d) => (
              <tr key={d.identification.id}>
                <td className="border px-2 py-1">
                  {d.identification.id}
                </td>
                <td className="border px-2 py-1">
                  {d.identification.name}
                </td>
                <td className="border px-2 py-1">{d.ipAddress}</td>
                <td className="border px-2 py-1">
                  {d.mac ?? d.identification.mac ?? '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}

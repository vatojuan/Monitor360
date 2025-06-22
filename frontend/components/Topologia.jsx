// File: frontend/components/Topologia.jsx

import React, { useEffect, useState, useCallback } from 'react';
import ReactFlow, { MiniMap, Controls, Background } from 'react-flow-renderer';
import dagre from 'dagre';
import { Spinner } from '@/components/ui/Spinner';    // Ajustá import según tu proyecto
import { Alert } from '@/components/ui/Alert';        // Ajustá import según tu proyecto

// ──────────────────────────────
// Configuración Dagre
// ──────────────────────────────
const nodeWidth = 180;
const nodeHeight = 50;

function applyLayout(nodes, edges) {
  const g = new dagre.graphlib.Graph();
  g.setDefaultEdgeLabel(() => ({}));
  g.setGraph({ rankdir: 'LR' });

  nodes.forEach((n) => g.setNode(n.id, { width: nodeWidth, height: nodeHeight }));
  edges.forEach((e) => g.setEdge(e.source, e.target));
  dagre.layout(g);

  return nodes.map((node) => {
    const { x, y } = g.node(node.id);
    return {
      ...node,
      position: { x, y },
      sourcePosition: 'right',
      targetPosition: 'left',
    };
  });
}

// ──────────────────────────────
// Componente Topología
// ──────────────────────────────
export default function Topologia({ seedIps }) {
  const [rawNodes, setRawNodes] = useState(null);
  const [rawEdges, setRawEdges] = useState(null);
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 1) Fetch de la topología
  useEffect(() => {
    async function fetchTopology() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch('http://localhost:8000/api/monitoring/topology', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ip_list: seedIps }),
        });
        if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
        const data = await res.json();
        // Asumimos que el payload viene con data.nodes y data.edges
        setRawNodes(data.nodes || []);
        setRawEdges(data.edges || []);
      } catch (e) {
        console.error('Error fetching topology:', e);
        setError(e.message);
      } finally {
        setLoading(false);
      }
    }
    fetchTopology();
  }, [seedIps]);

  // 2) Map y layout una vez que rawNodes/rawEdges estén
  useEffect(() => {
    if (!Array.isArray(rawNodes) || !Array.isArray(rawEdges)) return;

    const mappedNodes = rawNodes.map((n) => {
      let bg = '#03a9f4', prefix = '';
      switch (n.type) {
        case 'router':
          bg = '#ffeb3b';
          prefix = n.status ? '🟢' : '🔴';
          break;
        case 'ap':
          bg = '#4caf50';
          prefix = '📡';
          break;
        case 'switch':
          bg = '#9c27b0';
          prefix = '🔀';
          break;
        default:
          prefix = n.signal != null ? `${Math.round(n.signal)}dBm` : '';
      }
      return {
        id: n.id,
        data: { label: `${prefix} ${n.label}`.trim(), full: n },
        style: {
          background: bg,
          padding: 8,
          borderRadius: 6,
          color: '#000',
          fontWeight: 500,
        },
      };
    });

    const mappedEdges = rawEdges.map((e) => ({
      id: `${e.source}-${e.target}`,
      source: e.source,
      target: e.target,
      animated: true,
      style: e.degraded
        ? { stroke: '#f44336', strokeWidth: 3 }
        : { stroke: '#555' },
    }));

    setNodes(applyLayout(mappedNodes, mappedEdges));
    setEdges(mappedEdges);
  }, [rawNodes, rawEdges]);

  const onNodeClick = useCallback((_, node) => setSelected(node.data.full), []);

  // 3) Renderizado con fallbacks
  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Spinner size="xl" />
      </div>
    );
  }

  if (error) {
    return <Alert severity="error">Error al cargar la topología: {error}</Alert>;
  }

  if (!Array.isArray(nodes) || nodes.length === 0) {
    return <Alert severity="warning">No se obtuvo topología o está vacía.</Alert>;
  }

  return (
    <div className="flex w-full h-full">
      <div className="flex-grow" style={{ width: '100%', height: '100%' }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodeClick={onNodeClick}
          fitView
          style={{ width: '100%', height: '100%' }}
        >
          <MiniMap nodeColor={(n) => n.style.background} nodeStrokeColor={(n) => n.style.background} />
          <Controls />
          <Background gap={14} />
        </ReactFlow>
      </div>
      {selected && (
        <aside className="w-80 bg-white text-black p-4 shadow-xl overflow-auto">
          <h2 className="text-lg font-bold mb-2">Detalles</h2>
          <p><strong>ID:</strong> {selected.id}</p>
          <p><strong>Tipo:</strong> {selected.type}</p>
          {selected.port && <p><strong>Puerto:</strong> {selected.port}</p>}
          {selected.link_speed && <p><strong>Link Speed:</strong> {selected.link_speed}</p>}
          {selected.degraded && (
            <p className="text-red-600 font-semibold">⚠ Enlace degradado</p>
          )}
          {selected.signal && <p><strong>Señal:</strong> {selected.signal} dBm</p>}
          <button
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded"
            onClick={() => setSelected(null)}
          >
            Cerrar
          </button>
        </aside>
      )}
    </div>
  );
}

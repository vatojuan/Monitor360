// File: frontend/pages/status.jsx
import React from 'react'
import Status from '../components/Status'

export default function StatusPage() {
  return (
    <main className="w-screen h-screen overflow-auto bg-gray-50">
      <h1 className="text-2xl font-bold p-4">Estado de la Red</h1>
      <Status />
    </main>
  )
}

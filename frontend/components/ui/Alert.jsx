// File: frontend/components/ui/Alert.jsx

export default function Alert({ severity = 'info', title, children }) {
  const colors = {
    info: 'bg-blue-100 text-blue-900',
    warning: 'bg-yellow-100 text-yellow-900',
    error: 'bg-red-100 text-red-900',
    success: 'bg-green-100 text-green-900',
  }[severity];

  return (
    <div className={`rounded p-4 shadow ${colors}`}>
      {title && <div className="font-bold mb-1">{title}</div>}
      <div>{children}</div>
    </div>
  );
}

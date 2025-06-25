// frontend/components/ui/Alert.jsx
export function Alert({ children, type = 'error' }) {
  const colors = {
    error: 'bg-red-100 text-red-700',
    info: 'bg-blue-100 text-blue-700',
    success: 'bg-green-100 text-green-700',
  };
  return (
    <div className={`p-3 rounded ${colors[type]} border-l-4 border-current`}>
      {children}
    </div>
  );
}

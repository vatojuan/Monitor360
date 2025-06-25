// frontend/components/ui/Spinner.jsx
export default function Spinner({ children }) {
  return (
    <div className="flex items-center gap-2 text-xl">
      <svg className="h-6 w-6 animate-spin" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" opacity=".25" />
        <path d="M22 12a10 10 0 0 1-10 10" stroke="currentColor" strokeWidth="4" />
      </svg>
      <span>{children}</span>
    </div>
  );
}

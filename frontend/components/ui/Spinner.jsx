// File: frontend/components/ui/Spinner.jsx

export default function Spinner({ size = 'md', children }) {
  // map size tokens to Tailwind classes
  const sizeMap = {
    sm: { svg: 'h-4 w-4', text: 'text-sm' },
    md: { svg: 'h-6 w-6', text: 'text-base' },
    lg: { svg: 'h-8 w-8', text: 'text-lg' },
    xl: { svg: 'h-10 w-10', text: 'text-xl' },
  };
  const { svg: svgClasses, text: textClass } = sizeMap[size] || sizeMap.md;

  return (
    <div className={`flex items-center gap-2 ${textClass}`}>
      <svg className={`animate-spin ${svgClasses}`} viewBox="0 0 24 24" fill="none">
        <circle
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
          opacity=".25"
        />
        <path d="M22 12a10 10 0 0 1-10 10" stroke="currentColor" strokeWidth="4" />
      </svg>
      {children && <span>{children}</span>}
    </div>
  );
}

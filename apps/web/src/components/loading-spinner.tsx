"use client";

interface LoadingSpinnerProps { size?: "sm" | "md" | "lg"; label?: string; }

export function LoadingSpinner({ size = "md", label }: LoadingSpinnerProps) {
  const sizeClass = size === "sm" ? "h-4 w-4" : size === "lg" ? "h-8 w-8" : "h-6 w-6";
  return (
    <div className="flex items-center justify-center gap-2 py-4">
      <div className={`${sizeClass} animate-spin rounded-full border-2 border-gray-300 border-t-blue-600`} />
      {label && <span className="text-sm text-gray-500">{label}</span>}
    </div>
  );
}

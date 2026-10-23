"use client";

interface CtaButtonProps { label: string; classes: string; icon: string | null;
  onClick: () => void; disabled?: boolean; loading?: boolean; }

export function CtaButton({ label, classes, icon, onClick, disabled, loading }: CtaButtonProps) {
  return (
    <button onClick={onClick} disabled={disabled || loading}
      className={`${classes} inline-flex items-center justify-center gap-2 disabled:opacity-50`}>
      {loading && <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />}
      {!loading && icon && <span>{icon}</span>}
      <span>{label}</span>
    </button>
  );
}

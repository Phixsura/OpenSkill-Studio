"use client";

interface InstallButtonProps { state: string; label: string; disabled: boolean;
  variant: string; onClick: () => void; }

const variants: Record<string, string> = {
  primary: "bg-blue-600 text-white hover:bg-blue-700",
  secondary: "bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-300",
  warning: "bg-yellow-500 text-white hover:bg-yellow-600",
};

export function InstallButton({ state, label, disabled, variant, onClick }: InstallButtonProps) {
  return (
    <button onClick={onClick} disabled={disabled}
      className={`rounded-lg px-6 py-2.5 text-sm font-medium transition disabled:opacity-60 disabled:cursor-not-allowed ${variants[variant] ?? variants.primary}`}>
      {state === "installed" && "✓ "}{label}
    </button>
  );
}

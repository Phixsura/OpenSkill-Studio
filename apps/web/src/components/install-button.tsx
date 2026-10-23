"use client";

interface InstallButtonProps { label: string; icon: string; variant: string;
  disabled: boolean; secondaryLabel?: string;
  onPrimary: () => void; onSecondary?: () => void; permissionsCount?: number; }

const variantStyle: Record<string, string> = {
  install: "bg-blue-600 text-white hover:bg-blue-700",
  installed: "bg-green-50 text-green-700 border border-green-300 dark:bg-green-900/20 dark:border-green-700",
  loading: "bg-gray-200 text-gray-500 dark:bg-gray-700",
};

export function InstallButton({ label, icon, variant, disabled, secondaryLabel,
  onPrimary, onSecondary, permissionsCount }: InstallButtonProps) {
  return (
    <div className="space-y-1">
      <button onClick={onPrimary} disabled={disabled}
        className={`flex w-full items-center justify-center gap-2 rounded-lg py-2.5 text-sm font-semibold disabled:opacity-50 ${variantStyle[variant] ?? variantStyle.install}`}>
        <span>{icon}</span> {label}
      </button>
      {variant === "installed" && secondaryLabel && onSecondary && (
        <button onClick={onSecondary}
          className="w-full text-center text-xs text-gray-400 hover:text-red-500">
          {secondaryLabel}
        </button>
      )}
      {permissionsCount !== undefined && permissionsCount > 0 && variant === "install" && (
        <p className="text-center text-[10px] text-gray-400">Requires {permissionsCount} permissions</p>
      )}
    </div>
  );
}

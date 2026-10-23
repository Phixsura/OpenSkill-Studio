"use client";

interface SwitchToggleProps { label: string; description: string | null; enabled: boolean;
  disabled: boolean; ariaLabel: string; onToggle: () => void; }

export function SwitchToggle({ label, description, enabled, disabled, ariaLabel, onToggle }: SwitchToggleProps) {
  return (
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium">{label}</p>
        {description && <p className="text-xs text-gray-400">{description}</p>}
      </div>
      <button onClick={onToggle} disabled={disabled} aria-label={ariaLabel}
        className={`relative h-6 w-11 rounded-full transition-colors disabled:opacity-40 ${enabled ? "bg-blue-600" : "bg-gray-300 dark:bg-gray-600"}`}>
        <span className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform ${enabled ? "left-[1.375rem]" : "left-0.5"}`} />
      </button>
    </div>
  );
}

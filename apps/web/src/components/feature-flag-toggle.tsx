"use client";

interface FeatureFlagToggleProps {
  feature: string;
  enabled: boolean;
  onToggle: (feature: string, enabled: boolean) => void;
  description?: string;
}

export function FeatureFlagToggle({ feature, enabled, onToggle, description }: FeatureFlagToggleProps) {
  return (
    <div className="flex items-center justify-between rounded border border-gray-200 p-3 dark:border-gray-700">
      <div>
        <span className="text-sm font-medium">{feature.replace(/_/g, " ")}</span>
        {description && <p className="text-xs text-gray-500 dark:text-gray-400">{description}</p>}
      </div>
      <button
        onClick={() => onToggle(feature, !enabled)}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
          enabled ? "bg-green-500" : "bg-gray-300 dark:bg-gray-600"
        }`}
        role="switch"
        aria-checked={enabled}
      >
        <span className={`inline-block h-4 w-4 rounded-full bg-white transition-transform ${
          enabled ? "translate-x-6" : "translate-x-1"
        }`} />
      </button>
    </div>
  );
}

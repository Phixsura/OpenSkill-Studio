"use client";

interface RecoveryStrategy { strategy: string; description: string; icon: string; autoRecoverable: boolean; }
interface ErrorRecoveryPanelProps { strategy: RecoveryStrategy; retryCount: number; maxRetries: number;
  recoveryRate: number; totalErrors: number; }

export function ErrorRecoveryPanel({ strategy, retryCount, maxRetries, recoveryRate, totalErrors }: ErrorRecoveryPanelProps) {
  return (
    <div className="rounded-lg border p-4 dark:border-gray-700">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold">Error Recovery</h3>
        <span className="text-xs text-gray-400">{recoveryRate}% recovery rate</span>
      </div>
      <div className="flex items-center gap-3 rounded-lg bg-gray-50 p-3 dark:bg-gray-800">
        <span className="text-2xl">{strategy.icon}</span>
        <div>
          <p className="text-sm font-medium capitalize">{strategy.strategy.replace("_", " ")}</p>
          <p className="text-xs text-gray-400">{strategy.description}</p>
        </div>
        <span className={`ml-auto rounded px-2 py-0.5 text-xs ${strategy.autoRecoverable ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-red-100 text-red-700 dark:bg-red-900/30"}`}>
          {strategy.autoRecoverable ? "Auto" : "Manual"}
        </span>
      </div>
      <div className="mt-3 flex gap-4 text-xs text-gray-400">
        <span>Retries: {retryCount}/{maxRetries}</span>
        <span>Total errors: {totalErrors}</span>
      </div>
    </div>
  );
}

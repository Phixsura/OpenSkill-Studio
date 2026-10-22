"use client";

interface TimeoutAlertProps { functionName: string; timeoutSeconds: number; elapsedSeconds: number; }

export function TimeoutAlert({ functionName, timeoutSeconds, elapsedSeconds }: TimeoutAlertProps) {
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-800 dark:bg-red-900/20">
      <p className="font-semibold text-red-800 dark:text-red-200">⏰ Execution Timeout</p>
      <p className="mt-1 text-sm text-red-700 dark:text-red-300">
        Function <code className="font-mono">{functionName}</code> exceeded the {timeoutSeconds}s timeout (ran for {elapsedSeconds.toFixed(1)}s).
      </p>
    </div>
  );
}

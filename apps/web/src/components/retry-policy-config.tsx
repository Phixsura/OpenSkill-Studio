"use client";

interface RetryPolicyConfigProps { maxRetries: number; backoff: string;
  baseDelayMs: number; maxDelayMs: number; retryableCodes: number[];
  onChange: (field: string, value: unknown) => void; }

export function RetryPolicyConfig({ maxRetries, backoff, baseDelayMs, maxDelayMs, retryableCodes, onChange }: RetryPolicyConfigProps) {
  const delays = Array.from({ length: maxRetries }, (_, i) => {
    if (backoff === "exponential") return Math.min(baseDelayMs * (2 ** i), maxDelayMs);
    if (backoff === "linear") return Math.min(baseDelayMs * (i + 1), maxDelayMs);
    return baseDelayMs;
  });
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔄 Retry Policy</h3>
      </div>
      <div className="p-4 space-y-3">
        <div className="grid grid-cols-3 gap-3 text-xs">
          <div><span className="text-gray-400">Max Retries:</span> <span className="font-bold">{maxRetries}</span></div>
          <div><span className="text-gray-400">Backoff:</span> <span className="font-bold capitalize">{backoff}</span></div>
          <div><span className="text-gray-400">Base Delay:</span> <span className="font-bold">{baseDelayMs}ms</span></div>
        </div>
        <div>
          <div className="text-xs text-gray-400 mb-1">Delay Schedule</div>
          <div className="flex gap-1">
            {delays.map((d, i) => (
              <div key={i} className="flex-1 text-center">
                <div className="text-[10px] text-gray-400">#{i + 1}</div>
                <div className="text-xs font-mono font-bold">{d}ms</div>
              </div>
            ))}
          </div>
        </div>
        <div>
          <div className="text-xs text-gray-400 mb-1">Retryable Codes</div>
          <div className="flex gap-1 flex-wrap">
            {retryableCodes.map(c => (
              <span key={c} className="px-1.5 py-0.5 text-[10px] bg-gray-100 dark:bg-gray-800 rounded font-mono">{c}</span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

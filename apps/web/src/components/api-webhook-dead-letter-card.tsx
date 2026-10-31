"use client";

interface DeadLetterInfo {
  letter_id: string;
  destination: string;
  event_type: string;
  last_error: string;
  attempts: number;
  retried: boolean;
}

interface APIWebhookDeadLetterCardProps {
  letters: DeadLetterInfo[];
  appName: string;
}

export default function APIWebhookDeadLetterCard({ letters, appName }: APIWebhookDeadLetterCardProps) {
  const pending = letters.filter((l) => !l.retried).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">💀 Dead Letters</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-400">{letters.length} total</span>
          {pending > 0 && <p className="text-[10px] text-red-500">{pending} pending</p>}
        </div>
      </div>

      {letters.length === 0 ? (
        <p className="text-center text-sm text-green-600 dark:text-green-400">No dead letters</p>
      ) : (
        <div className="space-y-1.5">
          {letters.map((l) => (
            <div key={l.letter_id} className={`rounded-lg border border-gray-100 px-3 py-1.5 dark:border-gray-800 ${l.retried ? "opacity-50" : ""}`}>
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-700 dark:text-gray-300">{l.event_type}</span>
                <span className="text-[10px] text-gray-400">{l.attempts} attempts</span>
              </div>
              <p className="mt-0.5 text-[10px] text-red-500">{l.last_error}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

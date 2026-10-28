"use client";

interface RunbookStepInfo {
  instruction: string;
  expected_outcome: string;
}

interface RunbookInfo {
  runbook_id: string;
  title: string;
  description: string;
  steps: RunbookStepInfo[];
  tags: string[];
  execution_count: number;
}

interface RunbookCardProps {
  runbooks: RunbookInfo[];
  appName: string;
}

export default function RunbookCard({ runbooks, appName }: RunbookCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">📋 Runbooks</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-xs text-gray-400">{runbooks.length} runbooks</span>
      </div>

      {runbooks.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No runbooks</p>
      ) : (
        <div className="space-y-2">
          {runbooks.map((r) => (
            <div
              key={r.runbook_id}
              className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-800 dark:text-gray-200">
                  {r.title}
                </span>
                <span className="text-[11px] text-gray-400">
                  {r.steps.length} steps · {r.execution_count} runs
                </span>
              </div>
              {r.tags.length > 0 && (
                <div className="mt-1 flex gap-1">
                  {r.tags.map((t) => (
                    <span
                      key={t}
                      className="rounded bg-gray-100 px-1 py-0.5 text-[9px] text-gray-500 dark:bg-gray-800"
                    >
                      {t}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

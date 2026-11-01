"use client";

interface ReviewCheck {
  name: string;
  passed: boolean;
  message: string;
  warning?: boolean;
}

interface ReviewChecklistProps {
  checks: ReviewCheck[];
  score: number;
  passed: boolean;
}

export function ReviewChecklist({ checks, score, passed }: ReviewChecklistProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="font-semibold">Automated Review</h3>
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">{score}%</span>
          <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
            passed ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200" 
                   : "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
          }`}>
            {passed ? "Passed" : "Failed"}
          </span>
        </div>
      </div>
      <ul className="space-y-2">
        {checks.map((check) => (
          <li key={check.name} className="flex items-start gap-2 text-sm">
            <span className="mt-0.5">
              {check.passed ? (check.warning ? "⚠️" : "✅") : "❌"}
            </span>
            <div>
              <span className="font-medium">{check.name.replace(/_/g, " ")}</span>
              <span className="ml-1 text-gray-500 dark:text-gray-400">— {check.message}</span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

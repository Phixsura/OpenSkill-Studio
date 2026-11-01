"use client";

interface CheckItem { id: string; label: string; auto: boolean; pass: boolean; }
interface SubmissionReviewProps { checks: CheckItem[]; passed: number; total: number;
  readyForReview: boolean; score: number; onSubmit: () => void; }

export function SubmissionReview({ checks, passed, total, readyForReview, score, onSubmit }: SubmissionReviewProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Submission Checklist</h3>
        <span className={`rounded px-2 py-0.5 text-xs ${readyForReview ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30"}`}>
          {score}% — {passed}/{total}
        </span>
      </div>
      <div className="space-y-1">
        {checks.map(c => (
          <div key={c.id} className="flex items-center justify-between rounded border px-3 py-2 dark:border-gray-700">
            <div className="flex items-center gap-2">
              <span className={c.pass ? "text-green-600" : "text-red-600"}>{c.pass ? "✓" : "✗"}</span>
              <span className="text-sm">{c.label}</span>
            </div>
            {c.auto && <span className="text-xs text-gray-400">auto</span>}
          </div>
        ))}
      </div>
      <button onClick={onSubmit} disabled={!readyForReview}
        className="w-full rounded bg-blue-600 py-2 text-sm text-white disabled:opacity-30">
        {readyForReview ? "Submit for Review" : "Complete checklist first"}
      </button>
    </div>
  );
}

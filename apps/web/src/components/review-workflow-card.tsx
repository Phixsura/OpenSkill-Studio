"use client";

interface ReviewInfo {
  submission_id: string;
  app_version: string;
  status: "pending" | "in_review" | "approved" | "rejected" | "changes_requested";
  reviewer: string;
  feedback: string;
}

interface ReviewWorkflowCardProps {
  submissions: ReviewInfo[];
  appName: string;
}

const STATUS_STYLES: Record<string, { icon: string; text: string }> = {
  pending: { icon: "⏳", text: "text-gray-500" },
  in_review: { icon: "🔍", text: "text-blue-600 dark:text-blue-400" },
  approved: { icon: "✅", text: "text-green-600 dark:text-green-400" },
  rejected: { icon: "❌", text: "text-red-600 dark:text-red-400" },
  changes_requested: { icon: "📝", text: "text-yellow-600 dark:text-yellow-400" },
};

export default function ReviewWorkflowCard({ submissions, appName }: ReviewWorkflowCardProps) {
  const pendingCount = submissions.filter(
    (s) => s.status === "pending" || s.status === "in_review",
  ).length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Review Workflow
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        {pendingCount > 0 && (
          <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
            {pendingCount} pending
          </span>
        )}
      </div>

      {submissions.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No submissions</p>
      ) : (
        <div className="space-y-2">
          {submissions.map((s) => {
            const st = STATUS_STYLES[s.status] ?? STATUS_STYLES.pending;
            return (
              <div
                key={s.submission_id}
                className="rounded-lg border border-gray-100 px-3 py-2 dark:border-gray-800"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span>{st.icon}</span>
                    <span className="font-mono text-xs text-gray-800 dark:text-gray-200">
                      v{s.app_version}
                    </span>
                    <span className={`text-xs font-medium capitalize ${st.text}`}>
                      {s.status.replace("_", " ")}
                    </span>
                  </div>
                  {s.reviewer && <span className="text-[11px] text-gray-400">{s.reviewer}</span>}
                </div>
                {s.feedback && <p className="mt-1 text-[11px] text-gray-500">{s.feedback}</p>}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

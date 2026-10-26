"use client";

interface SubmissionChecklist {
  hasManifest: boolean;
  hasDescription: boolean;
  hasIcon: boolean;
  hasScreenshots: boolean;
  hasPrivacyPolicy: boolean;
  passesSecurityScan: boolean;
  passesContentReview: boolean;
  completionPercent: number;
}

interface Submission {
  id: string;
  extensionName: string;
  version: string;
  status: "draft" | "submitted" | "in_review" | "changes_requested" | "approved" | "rejected" | "published";
  checklist: SubmissionChecklist;
  reviewerName?: string;
  reviewNotes?: string;
  rejectionReason?: string;
  revision: number;
}

const statusFlow = ["draft", "submitted", "in_review", "approved", "published"];
const statusConfig: Record<string, { color: string; label: string }> = {
  draft: { color: "bg-gray-100 text-gray-600 dark:bg-gray-800", label: "Draft" },
  submitted: { color: "bg-blue-100 text-blue-700 dark:bg-blue-900/30", label: "Submitted" },
  in_review: { color: "bg-purple-100 text-purple-700 dark:bg-purple-900/30", label: "In Review" },
  changes_requested: { color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30", label: "Changes" },
  approved: { color: "bg-green-100 text-green-700 dark:bg-green-900/30", label: "Approved" },
  rejected: { color: "bg-red-100 text-red-600 dark:bg-red-900/30", label: "Rejected" },
  published: { color: "bg-green-200 text-green-800 dark:bg-green-900/40", label: "Published" },
};

const checklistLabels: [keyof SubmissionChecklist, string][] = [
  ["hasManifest", "Valid manifest.json"],
  ["hasDescription", "Description added"],
  ["hasIcon", "Icon uploaded"],
  ["hasScreenshots", "Screenshots added"],
  ["hasPrivacyPolicy", "Privacy policy"],
  ["passesSecurityScan", "Security scan"],
  ["passesContentReview", "Content review"],
];

export function SubmissionWorkflowPanel({
  submission,
  onSubmit,
  onPublish,
}: {
  submission: Submission;
  onSubmit?: () => void;
  onPublish?: () => void;
}) {
  const cfg = statusConfig[submission.status];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">🚀 {submission.extensionName} v{submission.version}</h2>
        <span className={`text-xs px-2 py-1 rounded-full ${cfg.color}`}>{cfg.label}</span>
      </div>

      {submission.revision > 1 && (
        <span className="text-xs text-gray-400">Revision #{submission.revision}</span>
      )}

      {/* Progress steps */}
      <div className="flex gap-1">
        {statusFlow.map((step) => {
          const isActive = step === submission.status;
          const isPast = statusFlow.indexOf(step) < statusFlow.indexOf(submission.status);
          return (
            <div key={step} className={`flex-1 h-2 rounded-full ${isActive ? "bg-blue-500" : isPast ? "bg-green-500" : "bg-gray-200 dark:bg-gray-700"}`} />
          );
        })}
      </div>

      {/* Checklist */}
      <div>
        <div className="flex justify-between text-sm mb-1">
          <span className="font-medium">Checklist</span>
          <span className="text-gray-500">{submission.checklist.completionPercent}%</span>
        </div>
        <div className="space-y-1">
          {checklistLabels.map(([key, label]) => {
            const checked = submission.checklist[key] as boolean;
            return (
              <div key={key} className="flex items-center gap-2 text-sm">
                <span className={checked ? "text-green-600" : "text-gray-300"}>
                  {checked ? "✅" : "⬜"}
                </span>
                <span className={checked ? "" : "text-gray-400"}>{label}</span>
              </div>
            );
          })}
        </div>
      </div>

      {submission.reviewNotes && (
        <div className="text-sm bg-blue-50 dark:bg-blue-900/10 rounded-lg p-3">
          <span className="font-medium">Review Notes:</span> {submission.reviewNotes}
        </div>
      )}

      {submission.rejectionReason && (
        <div className="text-sm bg-red-50 dark:bg-red-900/10 rounded-lg p-3 text-red-700 dark:text-red-300">
          <span className="font-medium">Rejected:</span> {submission.rejectionReason}
        </div>
      )}

      <div className="flex gap-2">
        {submission.status === "draft" && submission.checklist.completionPercent === 100 && (
          <button onClick={onSubmit} className="flex-1 text-sm bg-blue-600 text-white py-2 rounded-lg">Submit for Review</button>
        )}
        {submission.status === "approved" && (
          <button onClick={onPublish} className="flex-1 text-sm bg-green-600 text-white py-2 rounded-lg">Publish to Marketplace</button>
        )}
      </div>
    </div>
  );
}

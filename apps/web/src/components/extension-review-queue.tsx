"use client";

import { useState } from "react";

interface ReviewItem {
  extensionId: string;
  name: string;
  author: string;
  version: string;
  submittedAt: string;
  state: "submitted" | "in_review";
  securityScore: number;
  codeSize: string;
}

export function ExtensionReviewQueue({
  items,
  onApprove,
  onReject,
  onStartReview,
}: {
  items: ReviewItem[];
  onApprove?: (id: string, notes: string) => void;
  onReject?: (id: string, reason: string) => void;
  onStartReview?: (id: string) => void;
}) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [notes, setNotes] = useState("");

  const submitted = items.filter((i) => i.state === "submitted");
  const inReview = items.filter((i) => i.state === "in_review");

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold">📋 Extension Review Queue</h2>

      <div className="flex gap-4 text-sm">
        <div className="rounded-lg bg-yellow-50 dark:bg-yellow-900/20 px-3 py-1.5 text-yellow-700 dark:text-yellow-300">
          ⏳ {submitted.length} awaiting review
        </div>
        <div className="rounded-lg bg-blue-50 dark:bg-blue-900/20 px-3 py-1.5 text-blue-700 dark:text-blue-300">
          🔍 {inReview.length} in review
        </div>
      </div>

      <div className="space-y-3">
        {items.map((item) => (
          <div
            key={item.extensionId}
            className={`rounded-xl border dark:border-gray-700 p-4 transition ${
              selectedId === item.extensionId ? "ring-2 ring-blue-500" : ""
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold">{item.name}</h3>
                  <span className="text-xs bg-gray-100 dark:bg-gray-800 rounded px-2 py-0.5">
                    v{item.version}
                  </span>
                  <span className={`text-xs rounded px-2 py-0.5 ${
                    item.state === "submitted"
                      ? "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300"
                      : "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300"
                  }`}>
                    {item.state === "submitted" ? "⏳ Submitted" : "🔍 In Review"}
                  </span>
                </div>
                <div className="text-sm text-gray-500">
                  by {item.author} · {item.codeSize} · Submitted {item.submittedAt}
                </div>
                <SecurityScore score={item.securityScore} />
              </div>

              <div className="flex gap-2">
                {item.state === "submitted" && (
                  <button
                    onClick={() => { setSelectedId(item.extensionId); onStartReview?.(item.extensionId); }}
                    className="rounded-lg bg-blue-600 text-white px-3 py-1.5 text-sm"
                  >
                    Start Review
                  </button>
                )}
                {item.state === "in_review" && (
                  <>
                    <button
                      onClick={() => onApprove?.(item.extensionId, notes)}
                      className="rounded-lg bg-green-600 text-white px-3 py-1.5 text-sm"
                    >
                      ✅ Approve
                    </button>
                    <button
                      onClick={() => onReject?.(item.extensionId, notes)}
                      className="rounded-lg bg-red-600 text-white px-3 py-1.5 text-sm"
                    >
                      ❌ Reject
                    </button>
                  </>
                )}
              </div>
            </div>

            {selectedId === item.extensionId && item.state === "in_review" && (
              <div className="mt-3 pt-3 border-t dark:border-gray-700">
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Review notes..."
                  className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm"
                  rows={2}
                />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function SecurityScore({ score }: { score: number }) {
  const color = score >= 90 ? "text-green-500" : score >= 70 ? "text-yellow-500" : "text-red-500";
  return (
    <div className="flex items-center gap-1 text-xs">
      <span className="text-gray-400">Security:</span>
      <span className={`font-bold ${color}`}>{score}/100</span>
    </div>
  );
}

"use client";

import { useState } from "react";

interface ReviewModeration {
  id: string;
  reviewId: string;
  author: string;
  content: string;
  rating: number;
  status: "pending" | "approved" | "rejected" | "flagged" | "appealed";
  autoFlags: string[];
  rejectionReason?: string;
  appealText?: string;
}

const statusConfig: Record<string, { color: string; label: string }> = {
  pending: { color: "bg-gray-100 text-gray-600 dark:bg-gray-800", label: "Pending" },
  approved: { color: "bg-green-100 text-green-700 dark:bg-green-900/30", label: "Approved" },
  rejected: { color: "bg-red-100 text-red-600 dark:bg-red-900/30", label: "Rejected" },
  flagged: { color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30", label: "Flagged" },
  appealed: { color: "bg-purple-100 text-purple-700 dark:bg-purple-900/30", label: "Appealed" },
};

export function ReviewModerationPanel({
  reviews,
  onApprove,
  onReject,
  filter: initialFilter,
}: {
  reviews: ReviewModeration[];
  onApprove?: (id: string) => void;
  onReject?: (id: string, reason: string) => void;
  filter?: string;
}) {
  const [filter, setFilter] = useState(initialFilter || "all");

  const filtered = filter === "all" ? reviews : reviews.filter((r) => r.status === filter);
  const stars = (n: number) => "★".repeat(n) + "☆".repeat(5 - n);

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-bold">🛡️ Review Moderation</h2>

      <div className="flex gap-1 flex-wrap">
        {["all", "flagged", "pending", "appealed", "approved", "rejected"].map((s) => (
          <button key={s} onClick={() => setFilter(s)}
            className={`text-xs px-2.5 py-1 rounded-full ${filter === s ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {s === "all" ? `All (${reviews.length})` : `${s} (${reviews.filter((r) => r.status === s).length})`}
          </button>
        ))}
      </div>

      <div className="space-y-2">
        {filtered.map((rev) => {
          const cfg = statusConfig[rev.status];
          return (
            <div key={rev.id} className="rounded-xl border dark:border-gray-700 p-4">
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <span className="text-yellow-500 text-sm">{stars(rev.rating)}</span>
                  <span className="text-xs text-gray-400">by {rev.author}</span>
                  <span className={`text-xs px-1.5 py-0.5 rounded-full ${cfg.color}`}>{cfg.label}</span>
                </div>
                {(rev.status === "flagged" || rev.status === "pending" || rev.status === "appealed") && (
                  <div className="flex gap-1">
                    <button onClick={() => onApprove?.(rev.id)}
                      className="text-xs bg-green-600 text-white px-2 py-1 rounded">Approve</button>
                    <button onClick={() => onReject?.(rev.id, "low_quality")}
                      className="text-xs bg-red-600 text-white px-2 py-1 rounded">Reject</button>
                  </div>
                )}
              </div>
              <p className="text-sm text-gray-700 dark:text-gray-300">{rev.content}</p>
              {rev.autoFlags.length > 0 && (
                <div className="flex gap-1 mt-1">
                  {rev.autoFlags.map((f) => (
                    <span key={f} className="text-xs bg-orange-100 dark:bg-orange-900/20 text-orange-600 px-1.5 py-0.5 rounded">⚠ {f}</span>
                  ))}
                </div>
              )}
              {rev.appealText && (
                <div className="mt-1 text-xs bg-purple-50 dark:bg-purple-900/10 rounded p-2 text-purple-700 dark:text-purple-300">
                  Appeal: {rev.appealText}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

"use client";

import { useState } from "react";

interface FeatureRequest {
  id: string;
  title: string;
  description: string;
  author: string;
  votes: number;
  status: "open" | "planned" | "in_progress" | "completed" | "declined";
  hasVoted: boolean;
  developerResponse?: string;
}

export function FeatureRequestBoard({
  requests,
  extensionName,
  onVote,
  onSubmit,
}: {
  requests: FeatureRequest[];
  extensionName: string;
  onVote?: (id: string) => void;
  onSubmit?: (title: string, description: string) => void;
}) {
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState("");
  const [desc, setDesc] = useState("");
  const [filter, setFilter] = useState<string>("all");

  const statusConfig: Record<string, { color: string; label: string }> = {
    open: { color: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300", label: "Open" },
    planned: { color: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300", label: "Planned" },
    in_progress: { color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300", label: "In Progress" },
    completed: { color: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300", label: "Done" },
    declined: { color: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300", label: "Declined" },
  };

  const filtered = filter === "all" ? requests : requests.filter((r) => r.status === filter);

  const handleSubmit = () => {
    if (title.trim() && desc.trim()) {
      onSubmit?.(title.trim(), desc.trim());
      setTitle(""); setDesc(""); setShowForm(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">💡 {extensionName} Feature Requests</h2>
        <button onClick={() => setShowForm(!showForm)}
          className="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg">
          + New Request
        </button>
      </div>

      {showForm && (
        <div className="rounded-lg border dark:border-gray-700 p-4 space-y-2 bg-gray-50 dark:bg-gray-900/50">
          <input type="text" value={title} onChange={(e) => setTitle(e.target.value)}
            placeholder="Feature title" className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm" />
          <textarea value={desc} onChange={(e) => setDesc(e.target.value)}
            placeholder="Describe the feature..." rows={3}
            className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm" />
          <button onClick={handleSubmit} className="text-sm bg-green-600 text-white px-4 py-1.5 rounded-lg">Submit</button>
        </div>
      )}

      <div className="flex gap-1">
        {["all", "open", "planned", "in_progress", "completed"].map((s) => (
          <button key={s} onClick={() => setFilter(s)}
            className={`text-xs px-2.5 py-1 rounded-full ${filter === s ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
            {s === "all" ? "All" : statusConfig[s]?.label || s}
          </button>
        ))}
      </div>

      <div className="space-y-2">
        {filtered.map((req) => (
          <div key={req.id} className="rounded-xl border dark:border-gray-700 p-4 flex gap-3">
            <button onClick={() => onVote?.(req.id)}
              className={`shrink-0 flex flex-col items-center w-12 py-1 rounded-lg border ${
                req.hasVoted ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-600" : "border-gray-200 dark:border-gray-700 text-gray-400"
              }`}>
              <span className="text-xs">▲</span>
              <span className="text-sm font-bold">{req.votes}</span>
            </button>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-sm">{req.title}</span>
                <span className={`text-xs px-1.5 py-0.5 rounded-full ${statusConfig[req.status].color}`}>
                  {statusConfig[req.status].label}
                </span>
              </div>
              <p className="text-xs text-gray-500 mt-0.5">{req.description}</p>
              <span className="text-xs text-gray-400">by {req.author}</span>
              {req.developerResponse && (
                <div className="mt-1 text-xs bg-blue-50 dark:bg-blue-900/10 rounded p-2 text-blue-700 dark:text-blue-300">
                  💬 {req.developerResponse}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

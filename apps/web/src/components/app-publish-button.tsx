"use client";

import { useState } from "react";

interface AppPublishButtonProps {
  appStatus: string;
  onPublish: () => Promise<void>;
  disabled?: boolean;
}

const PUBLISHABLE = new Set(["approved"]);

export function AppPublishButton({ appStatus, onPublish, disabled }: AppPublishButtonProps) {
  const [loading, setLoading] = useState(false);
  const canPublish = PUBLISHABLE.has(appStatus) && !disabled;

  const handlePublish = async () => {
    setLoading(true);
    try { await onPublish(); } finally { setLoading(false); }
  };

  if (!canPublish) {
    return (
      <button disabled className="rounded bg-gray-200 px-4 py-2 text-sm text-gray-500 cursor-not-allowed dark:bg-gray-800">
        {appStatus === "published" ? "Already Published" :
         appStatus === "submitted" ? "Awaiting Review" :
         `Cannot Publish (${appStatus})`}
      </button>
    );
  }

  return (
    <button onClick={handlePublish} disabled={loading}
      className="rounded bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50">
      {loading ? "Publishing..." : "🚀 Publish to Marketplace"}
    </button>
  );
}

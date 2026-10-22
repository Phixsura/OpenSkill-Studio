"use client";

import { useState } from "react";

interface EventReplayButtonProps {
  eventId: string;
  eventType: string;
  onReplay: (eventId: string) => Promise<void>;
  disabled?: boolean;
}

export function EventReplayButton({ eventId, eventType, onReplay, disabled }: EventReplayButtonProps) {
  const [status, setStatus] = useState<"idle" | "replaying" | "done" | "error">("idle");

  const handleReplay = async () => {
    setStatus("replaying");
    try {
      await onReplay(eventId);
      setStatus("done");
      setTimeout(() => setStatus("idle"), 3000);
    } catch {
      setStatus("error");
      setTimeout(() => setStatus("idle"), 3000);
    }
  };

  return (
    <button
      onClick={handleReplay}
      disabled={disabled || status === "replaying"}
      className={`inline-flex items-center gap-1 rounded px-2 py-1 text-xs font-medium transition-colors ${
        status === "done" ? "bg-green-100 text-green-800" :
        status === "error" ? "bg-red-100 text-red-800" :
        status === "replaying" ? "bg-blue-100 text-blue-800" :
        "bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300"
      } disabled:cursor-not-allowed disabled:opacity-50`}
      title={`Replay ${eventType}`}
    >
      {status === "replaying" ? "⏳ Replaying..." :
       status === "done" ? "✅ Sent" :
       status === "error" ? "❌ Failed" :
       "🔄 Replay"}
    </button>
  );
}

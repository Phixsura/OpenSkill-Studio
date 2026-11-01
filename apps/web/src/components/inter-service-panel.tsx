"use client";

import { useState } from "react";

interface ServiceMessage {
  id: string;
  fromExtension: string;
  toExtension: string;
  messageType: "request" | "response" | "event" | "broadcast";
  channel: string;
  status: "queued" | "delivered" | "expired" | "rejected";
  timestamp: string;
}

interface ChannelAccess {
  channel: string;
  subscribed: boolean;
}

const typeIcons: Record<string, string> = {
  request: "📤", response: "📥", event: "⚡", broadcast: "📢",
};

const statusColors: Record<string, string> = {
  queued: "text-yellow-600", delivered: "text-green-600",
  expired: "text-gray-400", rejected: "text-red-600",
};

export function InterServicePanel({
  messages,
  channels,
  extensionName,
  onSubscribe,
  onSend,
}: {
  messages: ServiceMessage[];
  channels: ChannelAccess[];
  extensionName: string;
  onSubscribe?: (channel: string) => void;
  onSend?: (channel: string) => void;
}) {
  const [tab, setTab] = useState<"messages" | "channels">("messages");

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold">📡 {extensionName} IPC</h2>
        <span className="text-sm text-gray-500">{messages.length} messages</span>
      </div>

      <div className="flex gap-1">
        <button onClick={() => setTab("messages")}
          className={`text-xs px-3 py-1 rounded-lg ${tab === "messages" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          Messages
        </button>
        <button onClick={() => setTab("channels")}
          className={`text-xs px-3 py-1 rounded-lg ${tab === "channels" ? "bg-blue-600 text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-500"}`}>
          Channels ({channels.length})
        </button>
      </div>

      {tab === "messages" && (
        <div className="space-y-1">
          {messages.map((msg) => (
            <div key={msg.id} className="rounded-lg border dark:border-gray-700 p-2 flex items-center gap-2 text-sm">
              <span>{typeIcons[msg.messageType]}</span>
              <span className="font-mono text-xs">{msg.fromExtension}</span>
              <span className="text-gray-400">→</span>
              <span className="font-mono text-xs">{msg.toExtension}</span>
              <span className="text-xs bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">{msg.channel}</span>
              <span className={`text-xs ml-auto ${statusColors[msg.status]}`}>{msg.status}</span>
            </div>
          ))}
          {messages.length === 0 && <p className="text-sm text-gray-500">No messages</p>}
        </div>
      )}

      {tab === "channels" && (
        <div className="space-y-1">
          {channels.map((ch) => (
            <div key={ch.channel} className="flex items-center justify-between rounded-lg border dark:border-gray-700 p-3">
              <div className="flex items-center gap-2">
                <code className="text-sm">{ch.channel}</code>
                {ch.subscribed && <span className="text-xs text-green-600">● subscribed</span>}
              </div>
              <div className="flex gap-1">
                {!ch.subscribed && (
                  <button onClick={() => onSubscribe?.(ch.channel)}
                    className="text-xs bg-green-600 text-white px-2 py-1 rounded">Subscribe</button>
                )}
                <button onClick={() => onSend?.(ch.channel)}
                  className="text-xs bg-blue-600 text-white px-2 py-1 rounded">Send</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

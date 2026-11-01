"use client";

import { useState } from "react";

interface TicketMessage {
  authorId: string;
  authorName: string;
  body: string;
  timestamp: string;
  isInternal: boolean;
}

interface Ticket {
  id: string;
  subject: string;
  status: "open" | "in_progress" | "waiting_on_user" | "resolved" | "closed";
  priority: "low" | "medium" | "high" | "critical";
  reporter: string;
  assignee: string;
  category: string;
  createdAt: string;
  messages: TicketMessage[];
}

export function SupportTicketViewer({
  ticket,
  currentUserId,
  onReply,
  onResolve,
  onClose,
}: {
  ticket: Ticket;
  currentUserId: string;
  onReply?: (body: string) => void;
  onResolve?: () => void;
  onClose?: () => void;
}) {
  const [replyText, setReplyText] = useState("");

  const statusColors: Record<string, string> = {
    open: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300",
    in_progress: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300",
    waiting_on_user: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300",
    resolved: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300",
    closed: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300",
  };

  const priorityColors: Record<string, string> = {
    low: "text-gray-500", medium: "text-blue-500", high: "text-orange-500", critical: "text-red-500",
  };

  const handleReply = () => {
    if (replyText.trim()) {
      onReply?.(replyText.trim());
      setReplyText("");
    }
  };

  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden max-w-2xl">
      {/* Header */}
      <div className="bg-gray-50 dark:bg-gray-800 p-4 border-b dark:border-gray-700">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="font-bold text-lg">{ticket.subject}</h2>
            <div className="flex items-center gap-2 mt-1 text-sm">
              <span className={`text-xs px-2 py-0.5 rounded-full ${statusColors[ticket.status]}`}>
                {ticket.status.replace("_", " ")}
              </span>
              <span className={`text-xs font-medium ${priorityColors[ticket.priority]}`}>
                {ticket.priority.toUpperCase()}
              </span>
              <span className="text-gray-400">·</span>
              <span className="text-gray-500">{ticket.category}</span>
            </div>
          </div>
          <div className="text-xs text-gray-400 text-right">
            <div>Reporter: {ticket.reporter}</div>
            <div>Assignee: {ticket.assignee || "Unassigned"}</div>
            <div>{ticket.createdAt}</div>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="p-4 space-y-3 max-h-80 overflow-y-auto">
        {ticket.messages.filter(m => !m.isInternal || m.authorId === currentUserId).map((msg, i) => (
          <div key={i} className={`rounded-lg p-3 ${
            msg.authorId === currentUserId
              ? "bg-blue-50 dark:bg-blue-900/10 ml-8"
              : "bg-gray-50 dark:bg-gray-800 mr-8"
          }`}>
            <div className="flex justify-between text-xs text-gray-400 mb-1">
              <span className="font-medium">{msg.authorName}</span>
              <span>{msg.timestamp}</span>
            </div>
            <p className="text-sm">{msg.body}</p>
          </div>
        ))}
      </div>

      {/* Reply */}
      {ticket.status !== "closed" && (
        <div className="p-4 border-t dark:border-gray-700 space-y-2">
          <textarea
            value={replyText}
            onChange={(e) => setReplyText(e.target.value)}
            placeholder="Type your reply..."
            rows={2}
            className="w-full rounded-lg border dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm"
          />
          <div className="flex justify-between">
            <div className="flex gap-2">
              {ticket.status !== "resolved" && (
                <button onClick={onResolve} className="text-xs text-green-500 border border-green-300 dark:border-green-700 px-3 py-1 rounded">
                  ✅ Resolve
                </button>
              )}
              <button onClick={onClose} className="text-xs text-gray-500 border dark:border-gray-600 px-3 py-1 rounded">
                Close
              </button>
            </div>
            <button onClick={handleReply} className="text-sm bg-blue-600 text-white px-4 py-1.5 rounded-lg">
              Reply
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

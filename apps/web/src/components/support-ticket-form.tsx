"use client";

import { useState } from "react";

interface SupportTicketFormProps { onSubmit: (data: { subject: string; message: string; priority: string }) => void; }

export function SupportTicketForm({ onSubmit }: SupportTicketFormProps) {
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [priority, setPriority] = useState("medium");
  return (
    <div className="space-y-3 rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h4 className="font-semibold">🎫 New Support Ticket</h4>
      <input value={subject} onChange={e => setSubject(e.target.value)} placeholder="Subject"
        className="w-full rounded border px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800" />
      <textarea value={message} onChange={e => setMessage(e.target.value)} placeholder="Describe your issue..." rows={4}
        className="w-full rounded border px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800" />
      <div className="flex items-center gap-3">
        <select value={priority} onChange={e => setPriority(e.target.value)} className="rounded border px-2 py-1 text-sm dark:border-gray-600 dark:bg-gray-800">
          <option value="low">Low</option><option value="medium">Medium</option>
          <option value="high">High</option><option value="critical">Critical</option>
        </select>
        <button onClick={() => { if (subject && message) onSubmit({ subject, message, priority }); }}
          disabled={!subject || !message} className="rounded bg-blue-600 px-4 py-2 text-sm text-white disabled:opacity-50">Submit</button>
      </div>
    </div>
  );
}

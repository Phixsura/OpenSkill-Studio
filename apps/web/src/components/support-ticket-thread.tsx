"use client";
import { useState } from "react";

interface Message { senderId: string; content: string; sentAt: number; }
interface Ticket { ticketId: string; subject: string; priority: string; status: string; messages: Message[]; userId: string; }

const priorityColors: Record<string, string> = {
  urgent: "bg-red-500", high: "bg-orange-500", normal: "bg-blue-500", low: "bg-gray-400",
};

export function SupportTicketThread({ ticket, currentUserId, onReply, onClose }: {
  ticket: Ticket; currentUserId: string; onReply?: (content: string) => void; onClose?: () => void;
}) {
  const [reply, setReply] = useState("");
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${priorityColors[ticket.priority] || "bg-gray-400"}`} />
          <span className="font-bold text-sm">{ticket.subject}</span>
          <span className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded-full">{ticket.status}</span>
        </div>
        {ticket.status !== "closed" && <button onClick={onClose} className="text-xs text-gray-400">Close</button>}
      </div>
      <div className="space-y-2 max-h-64 overflow-y-auto">
        {ticket.messages.map((m, i) => {
          const isUser = m.senderId === ticket.userId;
          return (
            <div key={i} className={`rounded-xl p-3 text-sm ${isUser ? "bg-blue-50 dark:bg-blue-900/10 ml-8" : "bg-gray-50 dark:bg-gray-800 mr-8"}`}>
              <span className="text-xs font-medium text-gray-500 block mb-0.5">{isUser ? "You" : "Developer"}</span>
              {m.content}
            </div>
          );
        })}
      </div>
      {ticket.status !== "closed" && (
        <div className="flex gap-2">
          <input value={reply} onChange={e => setReply(e.target.value)} placeholder="Type a reply..."
            className="flex-1 border dark:border-gray-700 rounded-lg px-3 py-2 text-sm bg-transparent" />
          <button onClick={() => { onReply?.(reply); setReply(""); }} className="bg-blue-500 text-white px-3 py-2 rounded-lg text-sm">Send</button>
        </div>
      )}
    </div>
  );
}

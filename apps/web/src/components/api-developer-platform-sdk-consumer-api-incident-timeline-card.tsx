"use client";

import { useState } from "react";

interface EventInfo { type: string; message: string; time: string; }
interface IncidentInfo { id: string; title: string; severity: string; status: string; events: EventInfo[]; }

const SEV_COLOR: Record<string, string> = {
  p1: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
  p2: "bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300",
  p3: "bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300",
  p4: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
};

export default function IncidentTimelineCard() {
  const [incident] = useState<IncidentInfo>({
    id: "inc-42", title: "Payment API Timeout", severity: "p1", status: "active",
    events: [
      { type: "detected", message: "Error rate spike detected", time: "10:00" },
      { type: "investigating", message: "Checking payment gateway", time: "10:05" },
      { type: "identified", message: "Gateway rate limit hit", time: "10:15" },
    ],
  });

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">Incident Timeline</h3>
        <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${SEV_COLOR[incident.severity]}`}>{incident.severity}</span>
      </div>
      <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">{incident.title}</p>

      <div className="mt-4 space-y-2 border-l-2 border-zinc-200 pl-4 dark:border-zinc-700">
        {incident.events.map((e, i) => (
          <div key={i}>
            <div className="text-xs font-medium text-zinc-600 dark:text-zinc-400">{e.type} · {e.time}</div>
            <div className="text-sm text-zinc-800 dark:text-zinc-200">{e.message}</div>
          </div>
        ))}
      </div>

      <div className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
        {incident.events.length} events · {incident.status}
      </div>
    </div>
  );
}

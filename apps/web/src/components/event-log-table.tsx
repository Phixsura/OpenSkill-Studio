"use client";

interface EventLogEntry { eventId: string; eventType: string; status: string; timestamp: string; display: string; }

interface EventLogTableProps { entries: EventLogEntry[]; }

export function EventLogTable({ entries }: EventLogTableProps) {
  if (entries.length === 0) return <p className="py-3 text-center text-sm text-gray-400">No events logged</p>;
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm">
        <thead><tr className="border-b dark:border-gray-700">
          <th className="px-2 py-1">Event</th><th className="px-2 py-1">Status</th><th className="px-2 py-1">Time</th>
        </tr></thead>
        <tbody>{entries.map(e => (
          <tr key={e.eventId} className="border-b dark:border-gray-800">
            <td className="px-2 py-1 font-mono text-xs">{e.display}</td>
            <td className="px-2 py-1"><span className={`rounded px-1.5 py-0.5 text-xs ${e.status === "delivered" ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"}`}>{e.status}</span></td>
            <td className="px-2 py-1 text-xs text-gray-400">{e.timestamp}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>
  );
}

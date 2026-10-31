"use client";
import { useState } from "react";

interface ReportReason { id: string; label: string; }
interface ReportAppDialogProps { appName: string; reasons: ReportReason[];
  onSubmit: (reason: string, details: string) => void; onCancel: () => void; }

export function ReportAppDialog({ appName, reasons, onSubmit, onCancel }: ReportAppDialogProps) {
  const [reason, setReason] = useState("");
  const [details, setDetails] = useState("");
  return (
    <div className="rounded-xl border dark:border-gray-700 p-5 max-w-md shadow-xl bg-white dark:bg-gray-900">
      <h3 className="font-bold mb-1">🚩 Report {appName}</h3>
      <p className="text-xs text-gray-400 mb-3">Help us keep the marketplace safe</p>
      <div className="space-y-1.5 mb-3">
        {reasons.map(r => (
          <label key={r.id} className="flex items-center gap-2 text-sm cursor-pointer">
            <input type="radio" name="reason" value={r.id} checked={reason === r.id}
              onChange={() => setReason(r.id)} />
            {r.label}
          </label>
        ))}
      </div>
      <textarea value={details} onChange={e => setDetails(e.target.value)}
        placeholder="Additional details (optional)" rows={3}
        className="w-full text-xs px-3 py-2 border rounded mb-3 dark:bg-gray-800 dark:border-gray-600" />
      <div className="flex gap-2">
        <button onClick={onCancel} className="flex-1 py-2 border rounded text-sm">Cancel</button>
        <button onClick={() => reason && onSubmit(reason, details)} disabled={!reason}
          className="flex-1 py-2 bg-red-600 text-white text-sm rounded hover:bg-red-700 disabled:opacity-50">Submit Report</button>
      </div>
    </div>
  );
}

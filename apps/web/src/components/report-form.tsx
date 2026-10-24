"use client";

import { useState } from "react";

interface ReportFormProps { appName: string; reasons: { id: string; label: string }[];
  onSubmit: (reason: string, details: string) => void; onCancel: () => void; }

export function ReportForm({ appName, reasons, onSubmit, onCancel }: ReportFormProps) {
  const [reason, setReason] = useState("");
  const [details, setDetails] = useState("");

  return (
    <div className="mx-auto max-w-md space-y-4">
      <h2 className="text-lg font-bold">Report {appName}</h2>
      <p className="text-sm text-gray-500">Help us keep the marketplace safe.</p>
      <div className="space-y-1">
        {reasons.map(r => (
          <label key={r.id} className={`flex items-center gap-2 rounded border p-2 cursor-pointer ${reason === r.id ? "border-blue-500" : "dark:border-gray-700"}`}>
            <input type="radio" name="reason" checked={reason === r.id}
              onChange={() => setReason(r.id)} className="accent-blue-600" />
            <span className="text-sm">{r.label}</span>
          </label>
        ))}
      </div>
      <textarea value={details} onChange={e => setDetails(e.target.value)}
        placeholder="Additional details (optional)..." rows={3}
        className="w-full rounded border px-3 py-2 text-sm dark:bg-gray-800 dark:border-gray-600" />
      <div className="flex gap-3">
        <button onClick={onCancel} className="flex-1 rounded border py-2 text-sm dark:border-gray-700">Cancel</button>
        <button onClick={() => reason && onSubmit(reason, details)} disabled={!reason}
          className="flex-1 rounded bg-red-600 py-2 text-sm text-white disabled:opacity-30">Submit Report</button>
      </div>
    </div>
  );
}

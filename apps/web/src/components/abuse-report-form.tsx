"use client";

import { useState } from "react";

const REASONS = [
  { value: "spam", label: "Spam or misleading" },
  { value: "malware", label: "Malware or security risk" },
  { value: "copyright", label: "Copyright violation" },
  { value: "harassment", label: "Harassment or abuse" },
  { value: "other", label: "Other" },
];

interface AbuseReportFormProps { targetName: string; onSubmit: (reason: string, details: string) => void; onCancel: () => void; }

export function AbuseReportForm({ targetName, onSubmit, onCancel }: AbuseReportFormProps) {
  const [reason, setReason] = useState("");
  const [details, setDetails] = useState("");

  return (
    <div className="rounded-lg border border-gray-200 p-6 dark:border-gray-700">
      <h3 className="text-lg font-semibold">Report {targetName}</h3>
      <div className="mt-4 space-y-3">
        <div>
          <label className="block text-sm font-medium">Reason</label>
          <select value={reason} onChange={e => setReason(e.target.value)}
            className="mt-1 w-full rounded border p-2 text-sm dark:border-gray-600 dark:bg-gray-700">
            <option value="">Select a reason...</option>
            {REASONS.map(r => <option key={r.value} value={r.value}>{r.label}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium">Details</label>
          <textarea value={details} onChange={e => setDetails(e.target.value)} rows={4}
            placeholder="Describe the issue in detail..."
            className="mt-1 w-full rounded border p-2 text-sm dark:border-gray-600 dark:bg-gray-700" />
        </div>
      </div>
      <div className="mt-4 flex justify-end gap-3">
        <button onClick={onCancel} className="rounded px-4 py-2 text-sm text-gray-600 hover:bg-gray-100">Cancel</button>
        <button onClick={() => onSubmit(reason, details)} disabled={!reason || details.length < 10}
          className="rounded bg-red-600 px-4 py-2 text-sm text-white hover:bg-red-700 disabled:opacity-50">Submit Report</button>
      </div>
    </div>
  );
}

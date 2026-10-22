"use client";

import { useState } from "react";

const REASONS = ["spam", "malware", "phishing", "trademark", "inappropriate", "broken", "other"];

interface ReportAbuseFormProps { appName: string; onSubmit: (reason: string, details: string) => void; onCancel: () => void; }

export function ReportAbuseForm({ appName, onSubmit, onCancel }: ReportAbuseFormProps) {
  const [reason, setReason] = useState("");
  const [details, setDetails] = useState("");
  return (
    <div className="rounded-lg border border-red-200 p-4 dark:border-red-800">
      <h4 className="mb-2 font-semibold text-red-800 dark:text-red-200">🚩 Report {appName}</h4>
      <select value={reason} onChange={e => setReason(e.target.value)} className="mb-2 w-full rounded border px-2 py-1 text-sm dark:border-gray-600 dark:bg-gray-800">
        <option value="">Select reason...</option>
        {REASONS.map(r => <option key={r} value={r}>{r}</option>)}
      </select>
      <textarea value={details} onChange={e => setDetails(e.target.value)} placeholder="Additional details..." rows={3}
        className="mb-2 w-full rounded border px-2 py-1 text-sm dark:border-gray-600 dark:bg-gray-800" />
      <div className="flex gap-2">
        <button onClick={onCancel} className="rounded border px-3 py-1 text-sm">Cancel</button>
        <button onClick={() => onSubmit(reason, details)} disabled={!reason} className="rounded bg-red-600 px-3 py-1 text-sm text-white disabled:opacity-50">Submit Report</button>
      </div>
    </div>
  );
}

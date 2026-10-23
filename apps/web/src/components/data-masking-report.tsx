"use client";

interface PiiFindings { type: string; count: number; }
interface DataMaskingReportProps { masked: string; redactions: number; typesFound: string[]; }

const typeIcons: Record<string, string> = {
  email: "📧", phone: "📞", credit_card: "💳", ssn: "🔒", ip_address: "🌐",
};

export function DataMaskingReport({ masked, redactions, typesFound }: DataMaskingReportProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Data Masking</h3>
        <span className="text-xs text-gray-400">{redactions} redaction{redactions !== 1 ? "s" : ""}</span>
      </div>
      {typesFound.length > 0 && (
        <div className="flex gap-2">
          {typesFound.map(t => (
            <span key={t} className="flex items-center gap-1 rounded bg-red-50 px-2 py-0.5 text-xs text-red-700 dark:bg-red-900/20 dark:text-red-400">
              <span>{typeIcons[t] ?? "⚠"}</span>{t.replace("_", " ")}
            </span>
          ))}
        </div>
      )}
      <pre className="rounded-lg bg-gray-100 p-3 text-sm font-mono whitespace-pre-wrap dark:bg-gray-800">{masked}</pre>
    </div>
  );
}

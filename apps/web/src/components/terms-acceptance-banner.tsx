"use client";

interface PendingTerm { document_type: string; version: string; title?: string; url?: string; }
interface TermsAcceptanceBannerProps { pending: PendingTerm[]; onAccept: (docType: string, version: string) => void; }

export function TermsAcceptanceBanner({ pending, onAccept }: TermsAcceptanceBannerProps) {
  if (pending.length === 0) return null;
  return (
    <div className="space-y-2 rounded-lg border border-yellow-300 bg-yellow-50 p-4 dark:border-yellow-700 dark:bg-yellow-900/10">
      <h3 className="text-sm font-semibold text-yellow-800 dark:text-yellow-300">
        📋 Terms Update Required
      </h3>
      {pending.map(p => (
        <div key={`${p.document_type}-${p.version}`}
          className="flex items-center justify-between rounded border border-yellow-200 bg-white px-3 py-2 dark:border-yellow-800 dark:bg-gray-800">
          <div>
            <p className="text-sm font-medium">{p.title ?? p.document_type} v{p.version}</p>
            {p.url && <a href={p.url} target="_blank" rel="noopener noreferrer"
              className="text-xs text-blue-500 hover:underline">Read full document →</a>}
          </div>
          <button onClick={() => onAccept(p.document_type, p.version)}
            className="rounded bg-yellow-600 px-3 py-1 text-xs text-white">Accept</button>
        </div>
      ))}
    </div>
  );
}

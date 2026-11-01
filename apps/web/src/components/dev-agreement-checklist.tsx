"use client";

interface Agreement { id: string; title: string; version: string;
  required: boolean; accepted: boolean; outdated: boolean; }
interface DevAgreementChecklistProps { agreements: Agreement[];
  allAccepted: boolean; onAccept: (id: string) => void; }

export function DevAgreementChecklist({ agreements, allAccepted, onAccept }: DevAgreementChecklistProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 p-5">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold">📜 Developer Agreements</h3>
        <span className={`text-xs px-2 py-0.5 rounded-full ${allAccepted ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"}`}>
          {allAccepted ? "✅ All accepted" : "Action required"}
        </span>
      </div>
      <div className="space-y-2">
        {agreements.map(a => (
          <div key={a.id} className="flex items-center justify-between bg-gray-50 dark:bg-gray-800 rounded-lg px-4 py-2.5">
            <div>
              <span className="text-sm">{a.accepted ? "✅" : a.outdated ? "🔄" : "⬜"} {a.title}</span>
              <span className="text-xs text-gray-400 ml-2">v{a.version}</span>
              {a.required && !a.accepted && <span className="text-xs text-red-500 ml-1">Required</span>}
            </div>
            {!a.accepted && (
              <button onClick={() => onAccept(a.id)}
                className="text-xs px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">
                {a.outdated ? "Update" : "Accept"}
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

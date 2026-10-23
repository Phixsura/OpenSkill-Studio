"use client";

interface Section { key: string; title: string; icon: string; rights?: string[]; warning?: string; }
interface PrivacyCenterPageProps { userName: string; sections: Section[];
  onExportData: () => void; onDeleteAccount: () => void; }

export function PrivacyCenterPage({ userName, sections, onExportData, onDeleteAccount }: PrivacyCenterPageProps) {
  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold">Privacy Center</h1>
      <p className="text-sm text-gray-500">Manage your data and privacy settings, {userName}.</p>
      {sections.map(s => (
        <div key={s.key} className={`rounded-lg border p-4 ${s.key === "delete" ? "border-red-200 dark:border-red-800" : "border-gray-200 dark:border-gray-700"}`}>
          <h2 className="flex items-center gap-2 text-lg font-semibold">{s.icon} {s.title}</h2>
          {s.rights && (
            <ul className="mt-2 space-y-1">
              {s.rights.map((r, i) => <li key={i} className="text-sm text-gray-600 dark:text-gray-400">✓ {r}</li>)}
            </ul>
          )}
          {s.key === "data" && (
            <button onClick={onExportData} className="mt-3 rounded bg-blue-600 px-4 py-2 text-sm text-white">Export My Data</button>
          )}
          {s.key === "delete" && (
            <div className="mt-2">
              <p className="text-sm text-red-600">{s.warning}</p>
              <button onClick={onDeleteAccount} className="mt-2 rounded bg-red-600 px-4 py-2 text-sm text-white">Delete Account</button>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

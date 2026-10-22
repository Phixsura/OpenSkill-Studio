"use client";

interface InstallConfirmationProps {
  appName: string; developerName: string; verified: boolean; orgName: string;
  permissions: string[]; highRisk: string[]; onConfirm: () => void; onCancel: () => void;
}

export function InstallConfirmation({ appName, developerName, verified, orgName, permissions, highRisk, onConfirm, onCancel }: InstallConfirmationProps) {
  return (
    <div className="rounded-lg border border-gray-200 p-5 dark:border-gray-700">
      <h3 className="text-lg font-semibold">Install {appName}?</h3>
      <p className="text-sm text-gray-500">by {developerName} {verified ? "✓" : ""} → {orgName}</p>
      <div className="my-3">
        <p className="text-sm font-medium">Permissions ({permissions.length})</p>
        <ul className="mt-1 space-y-1">{permissions.map(p => (
          <li key={p} className={`text-sm ${highRisk.includes(p) ? "text-yellow-700 font-medium" : "text-gray-600"}`}>
            {highRisk.includes(p) ? "⚠️" : "✓"} {p}
          </li>
        ))}</ul>
      </div>
      <div className="flex gap-3">
        <button onClick={onCancel} className="rounded border px-4 py-2 text-sm">Cancel</button>
        <button onClick={onConfirm} className="rounded bg-blue-600 px-4 py-2 text-sm text-white">Install</button>
      </div>
    </div>
  );
}

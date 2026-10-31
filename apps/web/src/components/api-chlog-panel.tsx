"use client";
interface ApiChlogPanelProps { version: string; addedPaths: string[]; removedPaths: string[];
  modifiedCount: number; breaking: boolean; }
export function ApiChlogPanel({ version, addedPaths, removedPaths, modifiedCount, breaking }: ApiChlogPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📖 API Changelog</h3>
        <div className="flex items-center gap-2">
          {breaking && <span className="text-[10px] px-1.5 py-0.5 rounded bg-red-100 text-red-700">BREAKING</span>}
          <span className="text-xs text-gray-400">{version}</span>
        </div>
      </div>
      <div className="p-4 text-xs font-mono space-y-0.5">
        {addedPaths.map(p => <div key={p} className="text-green-600">+ {p}</div>)}
        {removedPaths.map(p => <div key={p} className="text-red-600">- {p}</div>)}
        {modifiedCount > 0 && <div className="text-yellow-600">~ {modifiedCount} modified</div>}
      </div>
    </div>
  );
}

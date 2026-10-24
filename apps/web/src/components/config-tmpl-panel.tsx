"use client";
interface ConfigTmplPanelProps { templateName: string; complete: boolean; usedVars: string[];
  missingVars: string[]; }
export function ConfigTmplPanel({ templateName, complete, usedVars, missingVars }: ConfigTmplPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">📝 Config Template</h3>
        <span className={`text-xs font-bold ${complete ? "text-green-600" : "text-red-500"}`}>
          {complete ? "✅ Complete" : `❌ ${missingVars.length} missing`} · {templateName}
        </span>
      </div>
      <div className="p-4 text-xs space-y-1">
        <div className="text-gray-400">Used: {usedVars.join(", ") || "none"}</div>
        {missingVars.length > 0 && <div className="text-red-500">Missing: {missingVars.join(", ")}</div>}
      </div>
    </div>
  );
}

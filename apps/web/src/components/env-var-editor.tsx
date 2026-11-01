"use client";

interface EnvVar { key: string; value: string; secret: boolean; }
interface EnvVarEditorProps { vars: EnvVar[]; onSet: (key: string, value: string) => void;
  onDelete: (key: string) => void; }

export function EnvVarEditor({ vars, onSet, onDelete }: EnvVarEditorProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">⚙️ Environment Variables</h3>
        <span className="text-xs text-gray-400">{vars.length} vars</span>
      </div>
      <div className="divide-y dark:divide-gray-700">
        {vars.map(v => (
          <div key={v.key} className="flex items-center justify-between px-4 py-2.5">
            <div className="flex items-center gap-2">
              <span className="text-sm font-mono font-medium">{v.key}</span>
              {v.secret && <span className="text-[10px] text-yellow-600">🔒</span>}
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono text-gray-400 max-w-[200px] truncate">{v.value}</span>
              <button onClick={() => onDelete(v.key)} className="text-xs text-red-500 hover:underline">×</button>
            </div>
          </div>
        ))}
      </div>
      <div className="p-3 border-t dark:border-gray-700">
        <button onClick={() => onSet("", "")}
          className="w-full py-1.5 text-xs text-blue-500 border border-dashed border-blue-300 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/10">
          + Add Variable
        </button>
      </div>
    </div>
  );
}

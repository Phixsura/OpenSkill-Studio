"use client";
interface EnvVar { key: string; value: string; secret: boolean; }
interface EnvConfigEditorProps { variables: EnvVar[]; secretCount: number; }
export function EnvConfigEditor({ variables, secretCount }: EnvConfigEditorProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">⚙️ Environment Variables</h3>
        <span className="text-xs text-gray-400">{variables.length} vars · {secretCount} secrets</span>
      </div>
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {variables.map(v => (
          <div key={v.key} className="flex items-center justify-between px-4 py-2">
            <code className="text-sm font-mono">{v.key}</code>
            <span className={`text-xs font-mono ${v.secret ? "text-yellow-600" : "text-gray-400"}`}>{v.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

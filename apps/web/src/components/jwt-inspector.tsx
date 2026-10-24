"use client";

interface JwtInspectorProps { valid: boolean; algorithm: string; expired: boolean;
  header: Record<string, unknown>; payload: Record<string, unknown>;
  standardClaims: string[]; customClaims: string[]; }

export function JwtInspector({ valid, algorithm, expired, header, payload, standardClaims, customClaims }: JwtInspectorProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔑 JWT Inspector</h3>
        <div className="flex gap-2 text-xs">
          <span className={valid ? "text-green-600" : "text-red-500"}>{valid ? "✅ Valid" : "❌ Invalid"}</span>
          <span className="text-gray-400">{algorithm}</span>
          {expired && <span className="text-red-500">⏰ Expired</span>}
        </div>
      </div>
      <div className="grid grid-cols-2 divide-x dark:divide-gray-700">
        <div className="p-3">
          <div className="text-[10px] text-gray-400 mb-1">Header</div>
          <pre className="text-[10px] font-mono">{JSON.stringify(header, null, 2)}</pre>
        </div>
        <div className="p-3">
          <div className="text-[10px] text-gray-400 mb-1">Payload</div>
          <pre className="text-[10px] font-mono">{JSON.stringify(payload, null, 2)}</pre>
        </div>
      </div>
      <div className="p-3 border-t dark:border-gray-700 flex gap-2 flex-wrap text-[10px]">
        {standardClaims.map(c => <span key={c} className="px-1.5 py-0.5 bg-blue-100 text-blue-700 rounded">{c}</span>)}
        {customClaims.map(c => <span key={c} className="px-1.5 py-0.5 bg-purple-100 text-purple-700 rounded">{c}</span>)}
      </div>
    </div>
  );
}

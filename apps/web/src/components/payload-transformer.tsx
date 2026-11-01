"use client";

interface PayloadTransformerProps { original: Record<string, unknown>;
  transformed: Record<string, unknown>; mappedFields: number; nullFields: number; }

export function PayloadTransformer({ original, transformed, mappedFields, nullFields }: PayloadTransformerProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔄 Payload Transformer</h3>
        <span className="text-xs text-gray-400">{mappedFields} mapped · {nullFields} null</span>
      </div>
      <div className="grid grid-cols-2 divide-x dark:divide-gray-700">
        <div className="p-3">
          <div className="text-[10px] text-gray-400 mb-1">Input</div>
          <pre className="text-[10px] font-mono text-gray-600 dark:text-gray-300 overflow-x-auto">
            {JSON.stringify(original, null, 2)}
          </pre>
        </div>
        <div className="p-3">
          <div className="text-[10px] text-gray-400 mb-1">Output</div>
          <pre className="text-[10px] font-mono text-green-600 dark:text-green-400 overflow-x-auto">
            {JSON.stringify(transformed, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  );
}

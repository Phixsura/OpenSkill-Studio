"use client";

interface PayloadTransformerEditorProps {
  inputPayload: string; outputPayload: string;
  onTransform: (input: string) => void; }

export function PayloadTransformerEditor({ inputPayload, outputPayload, onTransform }: PayloadTransformerEditorProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">🔄 Payload Transformer</h3>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1">Input</label>
          <textarea value={inputPayload} onChange={e => onTransform(e.target.value)}
            rows={6} className="w-full text-xs font-mono px-3 py-2 border rounded dark:bg-gray-800 dark:border-gray-600" />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-400 mb-1">Output</label>
          <pre className="text-xs font-mono px-3 py-2 bg-gray-50 dark:bg-gray-800 border rounded h-[144px] overflow-auto dark:border-gray-600">{outputPayload}</pre>
        </div>
      </div>
    </div>
  );
}

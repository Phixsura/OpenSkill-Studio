"use client";
interface WhTransformPanelProps { fieldsMapped: number; fieldsMissing: number; payloadSize: number; }
export function WhTransformPanel({ fieldsMapped, fieldsMissing, payloadSize }: WhTransformPanelProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700">
        <h3 className="font-semibold">🔄 Payload Transform</h3>
        <span className={`text-xs ${fieldsMissing > 0 ? "text-yellow-600" : "text-green-600"}`}>
          {fieldsMapped} mapped{fieldsMissing > 0 ? ` · ${fieldsMissing} missing` : ""} · {payloadSize}B
        </span>
      </div>
      <div className="grid grid-cols-3 gap-3 p-4 text-center text-xs">
        <div><span className="text-gray-400">Mapped</span><div className="font-bold text-green-600 text-lg">{fieldsMapped}</div></div>
        <div><span className="text-gray-400">Missing</span><div className={`font-bold text-lg ${fieldsMissing > 0 ? "text-yellow-600" : "text-gray-400"}`}>{fieldsMissing}</div></div>
        <div><span className="text-gray-400">Size</span><div className="font-bold text-lg">{payloadSize}B</div></div>
      </div>
    </div>
  );
}

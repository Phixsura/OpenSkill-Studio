"use client";

interface RuleInfo { field_pattern: string; mask_char: string; visible_chars: number; }
interface ConfigInfo { destination: string; rules: RuleInfo[]; masked_count: number; }
interface Props { configs: ConfigInfo[]; appName: string; }

export default function APIDeveloperPlatformSDKApiWebhookPayloadMaskingCard({ configs, appName }: Props) {
  const totalMasked = configs.reduce((s, c) => s + c.masked_count, 0);
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔒 Payload Masking</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-[10px] text-gray-400">{totalMasked.toLocaleString()} masked</span>
      </div>
      {configs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No masking configs</p>
      ) : (
        <div className="space-y-2">
          {configs.map((c) => (
            <div key={c.destination} className="rounded-lg bg-gray-50 p-2 dark:bg-gray-800">
              <div className="flex items-center justify-between text-[11px]">
                <span className="text-gray-700 dark:text-gray-300">{new URL(c.destination).hostname}</span>
                <span className="text-gray-400">{c.rules.length} rules · {c.masked_count} masked</span>
              </div>
              <div className="mt-0.5 flex flex-wrap gap-1">
                {c.rules.map((r) => (
                  <span key={r.field_pattern} className="rounded bg-red-50 px-1 py-0.5 text-[9px] text-red-700 dark:bg-red-900 dark:text-red-200">{r.field_pattern}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

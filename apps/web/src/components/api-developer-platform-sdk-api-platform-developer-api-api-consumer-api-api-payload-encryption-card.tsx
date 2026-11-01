"use client";

interface ConfigInfo { consumer_id: string; algorithm: string; encrypted_fields: string[]; }
interface Props { configs: ConfigInfo[]; totalEncrypted: number; totalFields: number; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiPayloadEncryptionCard({ configs, totalEncrypted, totalFields, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">🔐 Payload Encryption</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{appName}</p>
        </div>
        <span className="text-[10px] text-gray-400">{totalEncrypted.toLocaleString()} payloads · {totalFields.toLocaleString()} fields</span>
      </div>
      {configs.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No encryption configs</p>
      ) : (
        <div className="space-y-1.5">
          {configs.map((c) => (
            <div key={c.consumer_id} className="text-[11px]">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 dark:text-gray-300">{c.consumer_id}</span>
                <span className="rounded bg-purple-100 px-1 text-[9px] text-purple-700 dark:bg-purple-900/30 dark:text-purple-400">{c.algorithm}</span>
              </div>
              <div className="flex gap-1 mt-0.5">
                {c.encrypted_fields.map((f) => <span key={f} className="rounded bg-gray-100 px-1 text-[9px] text-gray-500 dark:bg-gray-800">🔒 {f}</span>)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

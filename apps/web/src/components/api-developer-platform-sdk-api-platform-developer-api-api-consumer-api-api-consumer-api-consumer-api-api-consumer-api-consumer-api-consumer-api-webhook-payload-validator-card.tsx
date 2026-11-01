"use client";

interface Schema { id: string; eventType: string; ruleCount: number; }
interface ValidationResult { eventType: string; valid: boolean; errors: string[]; sizeBytes: number; }
interface Props { schemas: Schema[]; lastValidation: ValidationResult | null; appName: string; }

export default function APIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiWebhookPayloadValidatorCard({ schemas, lastValidation, appName }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">✅ Payload Validator</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">{appName} — {schemas.length} schemas</p>
      </div>
      {lastValidation && (
        <div className={`mb-3 rounded-lg p-2 text-[11px] ${lastValidation.valid ? "bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-400" : "bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-400"}`}>
          {lastValidation.valid ? "✅ Valid" : "❌ Invalid"} — {lastValidation.eventType} ({lastValidation.sizeBytes} bytes)
          {lastValidation.errors.length > 0 && <div className="mt-0.5 text-[10px]">{lastValidation.errors.join(", ")}</div>}
        </div>
      )}
      {schemas.length === 0 ? (
        <p className="text-center text-sm text-gray-400">No schemas registered</p>
      ) : (
        <div className="space-y-0.5">
          {schemas.map((s) => (
            <div key={s.id} className="flex justify-between text-[11px]">
              <code className="text-gray-600 dark:text-gray-400">{s.eventType}</code>
              <span className="text-gray-400">{s.ruleCount} rules</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

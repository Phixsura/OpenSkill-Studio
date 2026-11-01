"use client";

interface ValidationError { field: string; error: string; message: string; }
interface RequestValidatorFormProps { valid: boolean | null; errors: ValidationError[];
  onValidate: (json: string) => void; }

export function RequestValidatorForm({ valid, errors, onValidate }: RequestValidatorFormProps) {
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700">
      <h3 className="font-semibold mb-3">✅ Request Validator</h3>
      <textarea rows={5} placeholder='{"name": "Alice", "email": "a@b.com"}'
        className="w-full text-xs font-mono px-3 py-2 border rounded mb-3 dark:bg-gray-800 dark:border-gray-600"
        onChange={e => onValidate(e.target.value)} />
      {valid !== null && (
        <div className={`p-3 rounded-lg text-sm ${valid ? "bg-green-50 text-green-700 dark:bg-green-900/20" : "bg-red-50 text-red-700 dark:bg-red-900/20"}`}>
          {valid ? "✅ Valid request" : `❌ ${errors.length} validation errors`}
        </div>
      )}
      {errors.length > 0 && (
        <div className="mt-2 space-y-1">
          {errors.map((e, i) => (
            <div key={i} className="text-xs text-red-600 flex gap-2">
              <span className="font-mono font-bold">{e.field}</span>
              <span>{e.message}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

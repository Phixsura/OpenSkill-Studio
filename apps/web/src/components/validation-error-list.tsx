"use client";

interface ValidationError { field: string; error: string; }
interface ValidationErrorListProps { errors: ValidationError[]; title?: string; }

export function ValidationErrorList({ errors, title = "Validation Errors" }: ValidationErrorListProps) {
  if (errors.length === 0) return null;
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-800 dark:bg-red-900/20">
      <h3 className="text-sm font-semibold text-red-800 dark:text-red-200">❌ {title}</h3>
      <ul className="mt-2 space-y-1">
        {errors.map((e, i) => (
          <li key={i} className="text-xs text-red-700 dark:text-red-300">
            <code className="font-semibold">{e.field}</code>: {e.error}
          </li>
        ))}
      </ul>
    </div>
  );
}

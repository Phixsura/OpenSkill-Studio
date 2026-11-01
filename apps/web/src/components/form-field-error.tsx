"use client";

interface FormFieldErrorProps { errors: string[]; touched: boolean; }

export function FormFieldError({ errors, touched }: FormFieldErrorProps) {
  if (!touched || errors.length === 0) return null;
  return (
    <div className="mt-1 space-y-0.5">
      {errors.map((err, i) => (
        <p key={i} className="text-xs text-red-500 flex items-center gap-1">
          <span>⚠</span>{err}
        </p>
      ))}
    </div>
  );
}

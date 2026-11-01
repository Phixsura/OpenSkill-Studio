"use client";

interface FormFieldWrapperProps { label: string; required?: boolean; error?: string; hint?: string; children: React.ReactNode; }

export function FormFieldWrapper({ label, required, error, hint, children }: FormFieldWrapperProps) {
  return (
    <div className="space-y-1">
      <label className="block text-sm font-medium">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      {children}
      {error && <p className="text-xs text-red-600">{error}</p>}
      {hint && !error && <p className="text-xs text-gray-400">{hint}</p>}
    </div>
  );
}

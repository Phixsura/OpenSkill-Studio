"use client";

interface TextInputFieldProps { name: string; label: string; type: string;
  placeholder: string; required: boolean; value: string; helpText: string | null;
  error: string | null; onChange: (value: string) => void; }

export function TextInputField({ name, label, type, placeholder, required, value,
  helpText, error, onChange }: TextInputFieldProps) {
  return (
    <div className="space-y-1">
      <label htmlFor={name} className="text-sm font-medium">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      <input id={name} name={name} type={type} value={value} placeholder={placeholder}
        required={required} onChange={e => onChange(e.target.value)}
        className={`w-full rounded-lg border px-4 py-2.5 text-sm ${error ? "border-red-500" : "dark:border-gray-600"} dark:bg-gray-700`}
        aria-label={label} />
      {helpText && !error && <p className="text-xs text-gray-400">{helpText}</p>}
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  );
}

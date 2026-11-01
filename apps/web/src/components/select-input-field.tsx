"use client";

interface Option { value: string; label: string; icon: string | null; disabled: boolean; }
interface SelectInputFieldProps { name: string; label: string; options: Option[];
  placeholder: string; required: boolean; value: string; error: string | null;
  onChange: (value: string) => void; }

export function SelectInputField({ name, label, options, placeholder, required,
  value, error, onChange }: SelectInputFieldProps) {
  return (
    <div className="space-y-1">
      <label htmlFor={name} className="text-sm font-medium">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      <select id={name} name={name} value={value} required={required}
        onChange={e => onChange(e.target.value)}
        className={`w-full rounded-lg border px-4 py-2.5 text-sm ${error ? "border-red-500" : "dark:border-gray-600"} dark:bg-gray-700`}>
        <option value="">{placeholder}</option>
        {options.map(opt => (
          <option key={opt.value} value={opt.value} disabled={opt.disabled}>
            {opt.icon ? `${opt.icon} ${opt.label}` : opt.label}
          </option>
        ))}
      </select>
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  );
}

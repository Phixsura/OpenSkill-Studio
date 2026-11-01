"use client";

interface RadioItem { value: string; label: string; description: string | null; icon: string | null; selected: boolean; }
interface RadioGroupProps { name: string; label: string; items: RadioItem[];
  onChange: (value: string) => void; }

export function RadioGroup({ name, label, items, onChange }: RadioGroupProps) {
  return (
    <fieldset className="space-y-2">
      <legend className="text-sm font-medium">{label}</legend>
      {items.map(item => (
        <label key={item.value}
          className={`flex cursor-pointer items-start gap-3 rounded-lg border p-3 ${item.selected ? "border-blue-500 bg-blue-50 dark:bg-blue-900/10" : "dark:border-gray-700"}`}>
          <input type="radio" name={name} value={item.value} checked={item.selected}
            onChange={() => onChange(item.value)} className="mt-0.5 accent-blue-600" />
          <div>
            <div className="flex items-center gap-1.5">
              {item.icon && <span>{item.icon}</span>}
              <span className="text-sm font-medium">{item.label}</span>
            </div>
            {item.description && <p className="mt-0.5 text-xs text-gray-400">{item.description}</p>}
          </div>
        </label>
      ))}
    </fieldset>
  );
}

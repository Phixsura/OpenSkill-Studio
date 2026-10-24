"use client";

interface CheckboxItem { value: string; label: string; checked: boolean; disabled: boolean; }
interface CheckboxGroupProps { name: string; label: string; items: CheckboxItem[];
  selectedCount: number; maxSelect: number | null;
  onToggle: (value: string) => void; }

export function CheckboxGroup({ name, label, items, selectedCount, maxSelect, onToggle }: CheckboxGroupProps) {
  return (
    <fieldset className="space-y-2">
      <legend className="text-sm font-medium">
        {label}
        {maxSelect && <span className="ml-1 text-xs text-gray-400">({selectedCount}/{maxSelect})</span>}
      </legend>
      {items.map(item => (
        <label key={item.value} className={`flex items-center gap-2 ${item.disabled ? "opacity-40" : "cursor-pointer"}`}>
          <input type="checkbox" name={name} value={item.value}
            checked={item.checked} disabled={item.disabled}
            onChange={() => onToggle(item.value)}
            className="h-4 w-4 rounded accent-blue-600" />
          <span className="text-sm">{item.label}</span>
        </label>
      ))}
    </fieldset>
  );
}

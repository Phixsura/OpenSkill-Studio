"use client";

interface SchemaField {
  name: string; label: string; type: string; required: boolean;
  default: unknown; description: string; enum: string[] | null;
  min: number | null; max: number | null;
}
interface JsonSchemaFormProps { fields: SchemaField[]; onSubmit: (data: Record<string, unknown>) => void; }

export function JsonSchemaForm({ fields, onSubmit }: JsonSchemaFormProps) {
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const data: Record<string, unknown> = {};
    fields.forEach(f => {
      if (f.type === "checkbox") data[f.name] = fd.get(f.name) === "on";
      else data[f.name] = fd.get(f.name) ?? f.default;
    });
    onSubmit(data);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {fields.map(f => (
        <div key={f.name}>
          <label className="block text-sm font-medium">
            {f.label} {f.required && <span className="text-red-500">*</span>}
          </label>
          {f.description && <p className="text-xs text-gray-400 mb-1">{f.description}</p>}
          {f.type === "select" && f.enum ? (
            <select name={f.name} defaultValue={String(f.default ?? "")}
              className="w-full rounded border px-3 py-2 text-sm dark:bg-gray-800 dark:border-gray-600">
              {f.enum.map(v => <option key={v} value={v}>{v}</option>)}
            </select>
          ) : f.type === "checkbox" ? (
            <input name={f.name} type="checkbox" defaultChecked={!!f.default} className="accent-blue-600" />
          ) : (
            <input name={f.name} type={f.type} required={f.required}
              defaultValue={f.default != null ? String(f.default) : ""}
              min={f.min ?? undefined} max={f.max ?? undefined}
              className="w-full rounded border px-3 py-2 text-sm dark:bg-gray-800 dark:border-gray-600" />
          )}
        </div>
      ))}
      <button type="submit" className="rounded bg-blue-600 px-4 py-2 text-sm text-white">Submit</button>
    </form>
  );
}

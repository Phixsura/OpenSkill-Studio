"use client";

interface SchemaField { name: string; type: string; label: string; required: boolean;
  default: unknown; description: string; options: string[] | null; }
interface ConfigSchemaEditorProps { fields: SchemaField[]; errors: string[]; valid: boolean; }

const typeIcons: Record<string, string> = {
  string: "📝", integer: "🔢", float: "🔢", boolean: "✅",
  select: "📋", secret: "🔒", url: "🔗", email: "📧",
};

export function ConfigSchemaEditor({ fields, errors, valid }: ConfigSchemaEditorProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Config Schema</h3>
        <span className={`rounded px-2 py-0.5 text-xs ${valid ? "bg-green-100 text-green-700 dark:bg-green-900/30" : "bg-red-100 text-red-700 dark:bg-red-900/30"}`}>
          {valid ? `✓ ${fields.length} fields` : `✗ ${errors.length} errors`}
        </span>
      </div>
      {errors.length > 0 && errors.map((e, i) => <p key={i} className="text-xs text-red-500">⚠ {e}</p>)}
      <div className="divide-y rounded-lg border dark:divide-gray-700 dark:border-gray-700">
        {fields.map(f => (
          <div key={f.name} className="px-4 py-2.5">
            <div className="flex items-center gap-2">
              <span>{typeIcons[f.type] ?? "📄"}</span>
              <code className="text-sm font-mono font-medium">{f.name}</code>
              <span className="rounded bg-gray-100 px-1.5 py-0.5 text-xs dark:bg-gray-800">{f.type}</span>
              {f.required && <span className="text-xs text-red-500">required</span>}
            </div>
            {f.description && <p className="mt-0.5 ml-6 text-xs text-gray-400">{f.description}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}

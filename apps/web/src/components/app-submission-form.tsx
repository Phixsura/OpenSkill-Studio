"use client";

interface ValidationError { field: string; error: string; }
interface AppSubmissionFormProps { onSubmit: (data: Record<string, string>) => void;
  errors: ValidationError[]; submitting: boolean; }

export function AppSubmissionForm({ onSubmit, errors, submitting }: AppSubmissionFormProps) {
  const fields = [
    { name: "name", label: "App Name", placeholder: "My Cool App" },
    { name: "description", label: "Description", placeholder: "What does your app do?", multiline: true },
    { name: "category", label: "Category", placeholder: "tools" },
    { name: "icon_url", label: "Icon URL", placeholder: "https://..." },
    { name: "developer_name", label: "Developer", placeholder: "Your company" },
  ];
  return (
    <div className="rounded-xl border p-5 dark:border-gray-700 max-w-lg">
      <h3 className="font-semibold mb-4">📤 Submit App</h3>
      <div className="space-y-3">
        {fields.map(f => {
          const err = errors.find(e => e.field === f.name);
          return (
            <div key={f.name}>
              <label className="block text-xs font-medium mb-1">{f.label}</label>
              {f.multiline ? (
                <textarea placeholder={f.placeholder} rows={3}
                  className="w-full text-sm px-3 py-1.5 border rounded dark:bg-gray-800 dark:border-gray-600" />
              ) : (
                <input placeholder={f.placeholder}
                  className="w-full text-sm px-3 py-1.5 border rounded dark:bg-gray-800 dark:border-gray-600" />
              )}
              {err && <p className="text-xs text-red-500 mt-0.5">{err.error}</p>}
            </div>
          );
        })}
      </div>
      <button onClick={() => onSubmit({})} disabled={submitting}
        className="w-full mt-4 py-2 bg-blue-600 text-white text-sm rounded font-medium hover:bg-blue-700 disabled:opacity-50">
        {submitting ? "Submitting..." : "Submit for Review"}
      </button>
    </div>
  );
}

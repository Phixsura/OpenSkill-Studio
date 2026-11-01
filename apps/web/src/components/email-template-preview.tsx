"use client";

interface EmailTemplatePreviewProps { subject: string; preheader: string; bodyHtml: string;
  templateId: string; }

export function EmailTemplatePreview({ subject, preheader, bodyHtml, templateId }: EmailTemplatePreviewProps) {
  return (
    <div className="rounded-xl border dark:border-gray-700 overflow-hidden">
      <div className="border-b bg-gray-50 px-4 py-3 dark:bg-gray-900 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-400 font-mono">{templateId}</span>
          <span className="text-xs text-gray-400">Preview</span>
        </div>
      </div>
      <div className="p-4">
        <div className="mb-3 space-y-1">
          <p className="text-xs text-gray-400">Subject</p>
          <p className="text-sm font-semibold">{subject}</p>
        </div>
        <div className="mb-3 space-y-1">
          <p className="text-xs text-gray-400">Preheader</p>
          <p className="text-sm text-gray-500">{preheader}</p>
        </div>
        {bodyHtml && (
          <div className="mt-3 rounded border p-3 dark:border-gray-700">
            <p className="text-xs text-gray-400 mb-1">Body</p>
            <iframe sandbox="" srcDoc={bodyHtml} className="w-full h-32 border-0 rounded" title="Email body preview" />
          </div>
        )}
      </div>
    </div>
  );
}

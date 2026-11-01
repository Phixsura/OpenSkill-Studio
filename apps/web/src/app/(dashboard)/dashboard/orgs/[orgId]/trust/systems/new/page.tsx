"use client";

import { useParams, useRouter } from "next/navigation";
import { useRef, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { apiWithAuth } from "@/lib/api";

const SYSTEM_TYPES = [
  { value: "workflow_pack", label: "Workflow Pack" },
  { value: "developer_app", label: "Developer App" },
  { value: "provider_binding", label: "Provider Binding" },
  { value: "evaluation_pipeline", label: "Evaluation Pipeline" },
  { value: "skill_pack", label: "Skill Pack" },
  { value: "custom", label: "Custom" },
];

export default function NewSystemPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const submitting = useRef(false);

  const [name, setName] = useState("");
  const [systemType, setSystemType] = useState("custom");
  const [description, setDescription] = useState("");
  const [error, setError] = useState("");

  const mutation = useMutation({
    mutationFn: () =>
      apiWithAuth(`/orgs/${orgId}/trust/systems`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: name.trim(),
          system_type: systemType,
          description: description.trim() || undefined,
        }),
      }),
    onSuccess: (data: { data: { id: string } }) => {
      queryClient.invalidateQueries({ queryKey: ["trust-systems"] });
      router.replace(`/dashboard/orgs/${orgId}/trust/systems/${data.data.id}`);
    },
    onError: (err: Error) => {
      setError(err?.message || "Failed to create system");
      submitting.current = false;
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting.current) return;
    submitting.current = true;
    setError("");
    mutation.mutate();
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold">Register AI System</h1>
      <p className="text-sm text-[hsl(var(--muted-foreground))]">
        Create a canonical record for an AI capability to track its risk, lifecycle, and intended uses.
      </p>

      {error && (
        <p className="rounded-md bg-red-50 p-3 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400">
          {error}
        </p>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Name *</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g., Content Moderation Pipeline"
            required
            maxLength={200}
            className="w-full rounded-md border px-3 py-2 text-sm bg-transparent focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium">System Type *</label>
          <select
            value={systemType}
            onChange={(e) => setSystemType(e.target.value)}
            className="w-full rounded-md border px-3 py-2 text-sm bg-transparent focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
          >
            {SYSTEM_TYPES.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium">Description</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Brief description of what this AI system does..."
            rows={4}
            className="w-full rounded-md border px-3 py-2 text-sm bg-transparent focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
          />
        </div>

        <div className="flex gap-3 pt-2">
          <button
            type="submit"
            disabled={!name.trim() || mutation.isPending}
            className="rounded-md bg-[hsl(var(--primary))] px-6 py-2 text-sm text-[hsl(var(--primary-foreground))] hover:opacity-90 disabled:opacity-50"
          >
            {mutation.isPending ? "Creating..." : "Register System"}
          </button>
          <button
            type="button"
            onClick={() => router.back()}
            className="rounded-md border px-6 py-2 text-sm hover:bg-[hsl(var(--secondary))]"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}

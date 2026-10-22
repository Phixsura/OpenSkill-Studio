"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, useEffect } from "react";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";

interface DeveloperAccount {
  id: string;
  display_name: string;
  slug: string;
  website_url: string | null;
  support_email: string;
  verified: boolean;
  status: string;
}

export default function DeveloperSettingsPage() {
  const queryClient = useQueryClient();

  const { data: account, isLoading } = useQuery({
    queryKey: ["developer-account-me"],
    queryFn: () =>
      apiWithAuth<{ data: DeveloperAccount }>("/developer/accounts/me").then((r) => r.data),
  });

  const [form, setForm] = useState({
    display_name: "",
    support_email: "",
    website_url: "",
  });

  useEffect(() => {
    if (account) {
      setForm({
        display_name: account.display_name,
        support_email: account.support_email,
        website_url: account.website_url ?? "",
      });
    }
  }, [account]);

  const updateMutation = useMutation({
    mutationFn: (data: Record<string, string | null>) =>
      apiWithAuth(`/developer/accounts/${account?.id}`, {
        method: "PATCH",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["developer-account-me"] });
    },
  });

  if (isLoading || !account) {
    return (
      <div className="p-8">
        <div className="h-8 w-48 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl p-8">
      <h1 className="mb-6 text-2xl font-bold">Developer Settings</h1>

      {/* Account info */}
      <div className="mb-6 rounded-lg border p-6 dark:border-gray-700">
        <h2 className="mb-4 text-lg font-semibold">Account Information</h2>
        <div className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium">Display Name</label>
            <input
              type="text"
              className="w-full rounded border px-3 py-2 dark:border-gray-600 dark:bg-gray-800"
              value={form.display_name}
              onChange={(e) => setForm({ ...form, display_name: e.target.value })}
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Support Email</label>
            <input
              type="email"
              className="w-full rounded border px-3 py-2 dark:border-gray-600 dark:bg-gray-800"
              value={form.support_email}
              onChange={(e) => setForm({ ...form, support_email: e.target.value })}
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Website</label>
            <input
              type="url"
              className="w-full rounded border px-3 py-2 dark:border-gray-600 dark:bg-gray-800"
              value={form.website_url}
              onChange={(e) => setForm({ ...form, website_url: e.target.value })}
              placeholder="https://your-company.com"
            />
          </div>
          <div className="flex items-center gap-3">
            <Button
              onClick={() =>
                updateMutation.mutate({
                  display_name: form.display_name,
                  support_email: form.support_email,
                  website_url: form.website_url || null,
                })
              }
              disabled={updateMutation.isPending}
            >
              {updateMutation.isPending ? "Saving..." : "Save Changes"}
            </Button>
            {updateMutation.isSuccess && (
              <span className="text-sm text-green-600">✓ Saved</span>
            )}
          </div>
        </div>
      </div>

      {/* Account status */}
      <div className="mb-6 rounded-lg border p-6 dark:border-gray-700">
        <h2 className="mb-4 text-lg font-semibold">Account Status</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-500">Slug</p>
            <p className="font-mono">@{account.slug}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Status</p>
            <p>
              <span
                className={`rounded px-2 py-0.5 text-sm ${
                  account.status === "active"
                    ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                    : "bg-red-100 text-red-800"
                }`}
              >
                {account.status}
              </span>
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Verified</p>
            <p>{account.verified ? "✅ Verified Publisher" : "Not verified"}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Account ID</p>
            <p className="font-mono text-xs text-gray-400">{account.id}</p>
          </div>
        </div>
      </div>

      {/* Danger zone */}
      <div className="rounded-lg border border-red-200 p-6 dark:border-red-800">
        <h2 className="mb-2 text-lg font-semibold text-red-600">Danger Zone</h2>
        <p className="mb-4 text-sm text-gray-500">
          These actions are irreversible and may affect your published apps.
        </p>
        <Button
          variant="destructive"
          disabled
          title="Contact support to deactivate your developer account"
        >
          Deactivate Account
        </Button>
        <p className="mt-2 text-xs text-gray-400">
          Contact support to deactivate your developer account
        </p>
      </div>
    </div>
  );
}

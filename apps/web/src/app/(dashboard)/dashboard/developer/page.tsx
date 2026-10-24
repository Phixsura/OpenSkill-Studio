"use client";

import Link from "next/link";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

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
  created_at: string;
}

export default function DeveloperPortalPage() {
  const queryClient = useQueryClient();
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({
    display_name: "",
    slug: "",
    support_email: "",
    website_url: "",
  });

  const { data: account, isLoading } = useQuery({
    queryKey: ["developer-account-me"],
    queryFn: () =>
      apiWithAuth<{ data: DeveloperAccount }>("/developer/accounts/me").then((r) => r.data),
    retry: false,
  });

  const createMutation = useMutation({
    mutationFn: (data: typeof form) =>
      apiWithAuth<{ data: DeveloperAccount }>("/developer/accounts", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["developer-account-me"] });
      setShowCreate(false);
    },
  });

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="h-8 w-48 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
      </div>
    );
  }

  // No developer account yet — show onboarding
  if (!account) {
    return (
      <div className="max-w-2xl p-8">
        <h1 className="mb-4 text-2xl font-bold">Developer Portal</h1>
        <p className="mb-6 text-gray-600 dark:text-gray-400">
          Create a developer account to build and distribute apps, connectors, and extensions on the
          OpenSkill platform.
        </p>

        {!showCreate ? (
          <Button onClick={() => setShowCreate(true)}>Create Developer Account</Button>
        ) : (
          <form
            onSubmit={(e) => {
              e.preventDefault();
              createMutation.mutate(form);
            }}
            className="space-y-4 rounded-lg border p-6 dark:border-gray-700"
          >
            <div>
              <label className="mb-1 block text-sm font-medium">Display Name</label>
              <input
                type="text"
                className="w-full rounded border px-3 py-2 dark:border-gray-600 dark:bg-gray-800"
                value={form.display_name}
                onChange={(e) => setForm({ ...form, display_name: e.target.value })}
                required
                minLength={2}
                maxLength={100}
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Slug</label>
              <input
                type="text"
                className="w-full rounded border px-3 py-2 dark:border-gray-600 dark:bg-gray-800"
                value={form.slug}
                onChange={(e) =>
                  setForm({
                    ...form,
                    slug: e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, ""),
                  })
                }
                required
                pattern="^[a-z0-9][a-z0-9-]*[a-z0-9]$"
                placeholder="my-developer-name"
              />
              <p className="mt-1 text-xs text-gray-500">
                URL-safe identifier (lowercase, hyphens allowed)
              </p>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Support Email</label>
              <input
                type="email"
                className="w-full rounded border px-3 py-2 dark:border-gray-600 dark:bg-gray-800"
                value={form.support_email}
                onChange={(e) => setForm({ ...form, support_email: e.target.value })}
                required
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Website (optional)</label>
              <input
                type="url"
                className="w-full rounded border px-3 py-2 dark:border-gray-600 dark:bg-gray-800"
                value={form.website_url}
                onChange={(e) => setForm({ ...form, website_url: e.target.value })}
              />
            </div>
            <div className="flex gap-2">
              <Button type="submit" disabled={createMutation.isPending}>
                {createMutation.isPending ? "Creating..." : "Create Account"}
              </Button>
              <Button type="button" variant="outline" onClick={() => setShowCreate(false)}>
                Cancel
              </Button>
            </div>
            {createMutation.isError && (
              <p className="text-sm text-red-600">{(createMutation.error as Error).message}</p>
            )}
          </form>
        )}
      </div>
    );
  }

  // Developer account exists — show dashboard
  return (
    <div className="p-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">{account.display_name}</h1>
          <p className="text-gray-500 dark:text-gray-400">
            @{account.slug}
            {account.verified && (
              <span className="ml-2 inline-flex items-center rounded bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                ✓ Verified
              </span>
            )}
          </p>
        </div>
      </div>

      <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-3">
        <Link
          href="/dashboard/developer/apps"
          className="block rounded-lg border p-6 transition-colors hover:border-blue-500 dark:border-gray-700"
        >
          <h3 className="mb-2 text-lg font-semibold">🧩 My Apps</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Create and manage your apps, connectors, and extensions
          </p>
        </Link>

        <Link
          href="/dashboard/developer/keys"
          className="block rounded-lg border p-6 transition-colors hover:border-blue-500 dark:border-gray-700"
        >
          <h3 className="mb-2 text-lg font-semibold">🔑 Signing Keys</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Manage Ed25519 keys for signing app packages
          </p>
        </Link>

        <Link
          href="/dashboard/developer/docs"
          className="block rounded-lg border p-6 transition-colors hover:border-blue-500 dark:border-gray-700"
        >
          <h3 className="mb-2 text-lg font-semibold">📖 Documentation</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            SDK guides, API reference, and best practices
          </p>
        </Link>
      </div>

      <div className="text-sm text-gray-500 dark:text-gray-400">
        <p>
          Support: {account.support_email}
          {account.website_url && (
            <>
              {" · "}
              <a
                href={account.website_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline"
              >
                {account.website_url}
              </a>
            </>
          )}
        </p>
        <p className="mt-1">Account created: {new Date(account.created_at).toLocaleDateString()}</p>
      </div>
    </div>
  );
}

"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { apiWithAuth } from "@/lib/api";

interface SigningKey {
  id: string;
  developer_id: string;
  fingerprint: string;
  name: string;
  is_primary: boolean;
  revoked_at: string | null;
  created_at: string;
}

export default function SigningKeysPage() {
  const queryClient = useQueryClient();
  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState({ name: "", public_key: "" });

  const { data, isLoading } = useQuery({
    queryKey: ["signing-keys"],
    queryFn: () => apiWithAuth<{ data: SigningKey[] }>("/developer/signing-keys"),
  });

  const addMutation = useMutation({
    mutationFn: (data: typeof form) =>
      apiWithAuth("/developer/signing-keys", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["signing-keys"] });
      setShowAdd(false);
      setForm({ name: "", public_key: "" });
    },
  });

  const keys = data?.data ?? [];

  return (
    <div className="max-w-3xl p-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Signing Keys</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Ed25519 public keys for signing app packages
          </p>
        </div>
        <Button onClick={() => setShowAdd(!showAdd)}>{showAdd ? "Cancel" : "+ Add Key"}</Button>
      </div>

      {showAdd && (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            addMutation.mutate(form);
          }}
          className="mb-6 space-y-4 rounded-lg border p-6 dark:border-gray-700"
        >
          <div>
            <label className="mb-1 block text-sm font-medium">Key Name</label>
            <input
              type="text"
              className="w-full rounded border px-3 py-2 dark:border-gray-600 dark:bg-gray-800"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              required
              placeholder="Production Key"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Public Key (Ed25519)</label>
            <textarea
              className="w-full rounded border px-3 py-2 font-mono text-sm dark:border-gray-600 dark:bg-gray-800"
              value={form.public_key}
              onChange={(e) => setForm({ ...form, public_key: e.target.value })}
              required
              rows={3}
              placeholder="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA..."
            />
          </div>
          <Button type="submit" disabled={addMutation.isPending}>
            {addMutation.isPending ? "Registering..." : "Register Key"}
          </Button>
          {addMutation.isError && (
            <p className="text-sm text-red-600">{(addMutation.error as Error).message}</p>
          )}
        </form>
      )}

      {isLoading ? (
        <div className="space-y-4">
          {[1, 2].map((i) => (
            <div key={i} className="h-16 animate-pulse rounded-lg bg-gray-200 dark:bg-gray-700" />
          ))}
        </div>
      ) : keys.length === 0 ? (
        <div className="py-12 text-center text-gray-500 dark:text-gray-400">
          <p className="mb-2 text-lg">No signing keys registered</p>
          <p className="text-sm">Register an Ed25519 public key to sign your app packages</p>
        </div>
      ) : (
        <div className="space-y-3">
          {keys.map((key) => (
            <div key={key.id} className="rounded-lg border p-4 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <span className="font-medium">{key.name}</span>
                  {key.is_primary && (
                    <span className="ml-2 rounded bg-blue-100 px-2 py-0.5 text-xs text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                      Primary
                    </span>
                  )}
                </div>
                <span className="text-xs text-gray-400">
                  {new Date(key.created_at).toLocaleDateString()}
                </span>
              </div>
              <p className="mt-1 font-mono text-sm text-gray-500 dark:text-gray-400">
                Fingerprint: {key.fingerprint}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

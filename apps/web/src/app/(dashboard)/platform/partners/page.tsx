"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { StatusBadge } from "@/components/status-badge";
import { apiWithAuth, ApiError } from "@/lib/api";
import { formatDate } from "@/lib/cp";

interface Partner {
  id: string;
  name: string;
  slug: string;
  partner_type: string;
  status: string;
  currency: string;
  contact_email: string | null;
  created_at: string;
}

const PARTNER_TYPES = [
  "reseller",
  "regional_operator",
  "school_channel",
  "content_partner",
  "workflow_partner",
  "referral",
];

export default function PlatformPartnersPage() {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [partnerType, setPartnerType] = useState("reseller");

  const { data, isLoading } = useQuery({
    queryKey: ["platform-partners"],
    queryFn: () => apiWithAuth<{ data: Partner[] }>("/platform/partners"),
  });
  const partners = data?.data ?? [];

  const createMutation = useMutation({
    mutationFn: () =>
      apiWithAuth("/platform/partners", {
        method: "POST",
        body: JSON.stringify({ name, slug, partner_type: partnerType }),
      }),
    onSuccess: () => {
      toast.success("Partner created");
      setShowForm(false);
      setName("");
      setSlug("");
      queryClient.invalidateQueries({ queryKey: ["platform-partners"] });
    },
    onError: (e) => toast.error(e instanceof ApiError ? e.message : "Create failed"),
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Partners</h2>
        <Button onClick={() => setShowForm(!showForm)}>{showForm ? "Close" : "New partner"}</Button>
      </div>

      {showForm && (
        <div className="flex flex-wrap gap-2 rounded-lg border p-4">
          <Input
            className="max-w-xs"
            placeholder="Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <Input
            className="max-w-[12rem]"
            placeholder="slug"
            value={slug}
            onChange={(e) => setSlug(e.target.value)}
          />
          <select
            className="rounded-md border bg-transparent px-3 py-2 text-sm"
            value={partnerType}
            onChange={(e) => setPartnerType(e.target.value)}
          >
            {PARTNER_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
          <Button
            onClick={() => createMutation.mutate()}
            disabled={!name || !slug || createMutation.isPending}
          >
            Create
          </Button>
        </div>
      )}

      {isLoading && <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>}
      {!isLoading && (
        <div className="overflow-x-auto rounded-lg border">
          <table className="w-full text-sm">
            <thead className="border-b bg-[hsl(var(--secondary))] text-left">
              <tr>
                <th className="px-4 py-2 font-medium">Name</th>
                <th className="px-4 py-2 font-medium">Type</th>
                <th className="px-4 py-2 font-medium">Status</th>
                <th className="px-4 py-2 font-medium">Currency</th>
                <th className="px-4 py-2 font-medium">Created</th>
              </tr>
            </thead>
            <tbody>
              {partners.map((p) => (
                <tr key={p.id} className="border-b last:border-0">
                  <td className="px-4 py-2">
                    <span className="font-medium">{p.name}</span>{" "}
                    <span className="font-mono text-xs text-[hsl(var(--muted-foreground))]">
                      {p.slug}
                    </span>
                  </td>
                  <td className="px-4 py-2">{p.partner_type}</td>
                  <td className="px-4 py-2">
                    <StatusBadge status={p.status} />
                  </td>
                  <td className="px-4 py-2">{p.currency}</td>
                  <td className="px-4 py-2">{formatDate(p.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

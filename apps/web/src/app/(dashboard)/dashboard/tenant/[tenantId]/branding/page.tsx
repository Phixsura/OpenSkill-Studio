"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiWithAuth, ApiError } from "@/lib/api";

interface Branding {
  product_display_name: string | null;
  login_tagline: string | null;
  email_from_name: string | null;
  email_footer: string | null;
  certificate_footer: string | null;
  support_email: string | null;
  support_url: string | null;
  theme_tokens: Record<string, string>;
  legal_links: { label: string; url: string }[];
}

const COLOR_KEYS = ["primary", "accent", "background", "foreground", "muted", "border"];
const RADIUS_VALUES = ["none", "sm", "md", "lg", "full"];

export default function TenantBrandingPage() {
  const { tenantId } = useParams<{ tenantId: string }>();
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["tenant-branding", tenantId],
    queryFn: () => apiWithAuth<{ data: Branding }>(`/tenants/${tenantId}/branding`),
  });

  const [form, setForm] = useState<Branding | null>(null);
  useEffect(() => {
    if (data?.data && form === null) {
      setForm({ ...data.data, theme_tokens: { ...data.data.theme_tokens } });
    }
  }, [data, form]);

  const saveMutation = useMutation({
    mutationFn: (payload: Partial<Branding>) =>
      apiWithAuth(`/tenants/${tenantId}/branding`, {
        method: "PUT",
        body: JSON.stringify(payload),
      }),
    onSuccess: () => {
      toast.success("Branding saved");
      queryClient.invalidateQueries({ queryKey: ["tenant-branding", tenantId] });
    },
    onError: (e) =>
      toast.error(
        e instanceof ApiError
          ? e.code === "FEATURE_NOT_AVAILABLE"
            ? "White-label branding requires a plan with the white_label feature."
            : e.message
          : "Save failed",
      ),
  });

  if (isLoading || !form) {
    return <p className="text-sm text-[hsl(var(--muted-foreground))]">Loading...</p>;
  }

  const set = (field: keyof Branding, value: string) =>
    setForm({ ...form, [field]: value || null });

  const setToken = (key: string, value: string) => {
    const tokens = { ...form.theme_tokens };
    if (value) tokens[key] = value;
    else delete tokens[key];
    setForm({ ...form, theme_tokens: tokens });
  };

  const handleSave = () => {
    saveMutation.mutate({
      product_display_name: form.product_display_name,
      login_tagline: form.login_tagline,
      email_from_name: form.email_from_name,
      email_footer: form.email_footer,
      certificate_footer: form.certificate_footer,
      support_email: form.support_email,
      support_url: form.support_url,
      theme_tokens: form.theme_tokens,
      legal_links: form.legal_links,
    });
  };

  return (
    <div className="max-w-2xl space-y-6">
      <section className="space-y-3">
        <h2 className="text-lg font-semibold">Identity</h2>
        <Field label="Product display name">
          <Input
            value={form.product_display_name ?? ""}
            onChange={(e) => set("product_display_name", e.target.value)}
            placeholder="Partner Academy"
            maxLength={100}
          />
        </Field>
        <Field label="Login tagline">
          <Input
            value={form.login_tagline ?? ""}
            onChange={(e) => set("login_tagline", e.target.value)}
            placeholder="Learn AI creation, hands-on"
            maxLength={200}
          />
        </Field>
        <Field label="Support email">
          <Input
            type="email"
            value={form.support_email ?? ""}
            onChange={(e) => set("support_email", e.target.value)}
          />
        </Field>
        <Field label="Support URL (https)">
          <Input
            value={form.support_url ?? ""}
            onChange={(e) => set("support_url", e.target.value)}
            placeholder="https://support.example.com"
          />
        </Field>
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-semibold">Theme</h2>
        <div className="grid gap-3 sm:grid-cols-2">
          {COLOR_KEYS.map((key) => (
            <Field key={key} label={key}>
              <div className="flex gap-2">
                <input
                  type="color"
                  className="h-9 w-12 cursor-pointer rounded border"
                  value={form.theme_tokens[key] ?? "#000000"}
                  onChange={(e) => setToken(key, e.target.value)}
                />
                <Input
                  value={form.theme_tokens[key] ?? ""}
                  onChange={(e) => setToken(key, e.target.value)}
                  placeholder="#1a2b3c"
                  maxLength={7}
                />
              </div>
            </Field>
          ))}
          <Field label="radius">
            <select
              className="w-full rounded-md border bg-transparent px-3 py-2 text-sm"
              value={form.theme_tokens.radius ?? ""}
              onChange={(e) => setToken("radius", e.target.value)}
            >
              <option value="">default</option>
              {RADIUS_VALUES.map((v) => (
                <option key={v} value={v}>
                  {v}
                </option>
              ))}
            </select>
          </Field>
        </div>
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-semibold">Email & certificates</h2>
        <Field label="Email from name">
          <Input
            value={form.email_from_name ?? ""}
            onChange={(e) => set("email_from_name", e.target.value)}
            maxLength={100}
          />
        </Field>
        <Field label="Email footer (plain text)">
          <Input
            value={form.email_footer ?? ""}
            onChange={(e) => set("email_footer", e.target.value)}
            maxLength={500}
          />
        </Field>
        <Field label="Certificate footer">
          <Input
            value={form.certificate_footer ?? ""}
            onChange={(e) => set("certificate_footer", e.target.value)}
            maxLength={300}
          />
        </Field>
      </section>

      <Button onClick={handleSave} disabled={saveMutation.isPending}>
        {saveMutation.isPending ? "Saving…" : "Save branding"}
      </Button>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block space-y-1">
      <span className="text-sm font-medium">{label}</span>
      {children}
    </label>
  );
}

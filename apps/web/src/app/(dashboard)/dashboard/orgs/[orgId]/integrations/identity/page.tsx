"use client";

// Enterprise identity console (ADR-018 §5): verified domains, SSO
// connections (OIDC), SCIM provisioning tokens, ambiguous-identity queue.

import { useState } from "react";
import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { apiWithAuth, ApiError } from "@/lib/api";

interface OrgDomain {
  id: string;
  domain: string;
  status: string;
  verification_token: string;
}

interface SsoConnection {
  id: string;
  protocol: string;
  status: string;
  oidc_issuer: string | null;
  oidc_client_id: string | null;
  has_client_secret: boolean;
  enforce_sso: boolean;
  allow_jit: boolean;
  default_role: string;
}

interface ScimToken {
  id: string;
  name: string;
  last_used_at: string | null;
  revoked_at: string | null;
  token?: string | null;
}

interface QueueItem {
  id: string;
  source: string;
  subject: string;
  email: string | null;
  reason: string;
  status: string;
}

export default function IdentityIntegrationsPage() {
  const { orgId } = useParams<{ orgId: string }>();
  const queryClient = useQueryClient();
  const base = `/orgs/${orgId}/integrations`;

  const [newDomain, setNewDomain] = useState("");
  const [issuer, setIssuer] = useState("");
  const [clientId, setClientId] = useState("");
  const [clientSecret, setClientSecret] = useState("");
  const [allowJit, setAllowJit] = useState(false);
  const [tokenName, setTokenName] = useState("");
  const [mintedToken, setMintedToken] = useState<string | null>(null);
  const [linkUserId, setLinkUserId] = useState("");

  const domainsQ = useQuery({
    queryKey: ["intg-domains", orgId],
    queryFn: () => apiWithAuth<{ data: OrgDomain[] }>(`${base}/domains`),
  });
  const ssoQ = useQuery({
    queryKey: ["intg-sso", orgId],
    queryFn: () => apiWithAuth<{ data: SsoConnection[] }>(`${base}/sso-connections`),
  });
  const tokensQ = useQuery({
    queryKey: ["intg-scim-tokens", orgId],
    queryFn: () => apiWithAuth<{ data: ScimToken[] }>(`${base}/scim-tokens`),
  });
  const queueQ = useQuery({
    queryKey: ["intg-id-queue", orgId],
    queryFn: () => apiWithAuth<{ data: QueueItem[] }>(`${base}/identity-queue`),
  });

  const onError = (err: unknown) =>
    toast.error(err instanceof ApiError ? err.message : "Request failed");

  const claimDomain = useMutation({
    mutationFn: () =>
      apiWithAuth(`${base}/domains`, {
        method: "POST",
        body: JSON.stringify({ domain: newDomain }),
      }),
    onSuccess: () => {
      toast.success("Domain claimed — add the TXT record, then verify");
      setNewDomain("");
      queryClient.invalidateQueries({ queryKey: ["intg-domains", orgId] });
    },
    onError,
  });

  const verifyDomain = useMutation({
    mutationFn: (id: string) => apiWithAuth(`${base}/domains/${id}/verify`, { method: "POST" }),
    onSuccess: () => {
      toast.success("Domain verified");
      queryClient.invalidateQueries({ queryKey: ["intg-domains", orgId] });
    },
    onError,
  });

  const createSso = useMutation({
    mutationFn: () =>
      apiWithAuth(`${base}/sso-connections`, {
        method: "POST",
        body: JSON.stringify({
          protocol: "oidc",
          oidc_issuer: issuer,
          oidc_client_id: clientId,
          oidc_client_secret: clientSecret || null,
          allow_jit: allowJit,
        }),
      }),
    onSuccess: () => {
      toast.success("SSO connection created (testing)");
      setIssuer("");
      setClientId("");
      setClientSecret("");
      queryClient.invalidateQueries({ queryKey: ["intg-sso", orgId] });
    },
    onError,
  });

  const patchSso = useMutation({
    mutationFn: (args: { id: string; body: Record<string, unknown> }) =>
      apiWithAuth(`${base}/sso-connections/${args.id}`, {
        method: "PATCH",
        body: JSON.stringify(args.body),
      }),
    onSuccess: () => {
      toast.success("SSO connection updated");
      queryClient.invalidateQueries({ queryKey: ["intg-sso", orgId] });
    },
    onError,
  });

  const mintToken = useMutation({
    mutationFn: () =>
      apiWithAuth<{ data: ScimToken }>(`${base}/scim-tokens`, {
        method: "POST",
        body: JSON.stringify({ name: tokenName, group_map: {} }),
      }),
    onSuccess: (res) => {
      setMintedToken(res.data.token ?? null);
      setTokenName("");
      queryClient.invalidateQueries({ queryKey: ["intg-scim-tokens", orgId] });
    },
    onError,
  });

  const revokeToken = useMutation({
    mutationFn: (id: string) => apiWithAuth(`${base}/scim-tokens/${id}`, { method: "DELETE" }),
    onSuccess: () => {
      toast.success("Token revoked");
      queryClient.invalidateQueries({ queryKey: ["intg-scim-tokens", orgId] });
    },
    onError,
  });

  const resolveQueue = useMutation({
    mutationFn: (args: { id: string; action: "link" | "reject"; user_id?: string }) =>
      apiWithAuth(`${base}/identity-queue/${args.id}/resolve`, {
        method: "POST",
        body: JSON.stringify({ action: args.action, user_id: args.user_id ?? null }),
      }),
    onSuccess: () => {
      toast.success("Resolved");
      queryClient.invalidateQueries({ queryKey: ["intg-id-queue", orgId] });
    },
    onError,
  });

  return (
    <div className="space-y-8 p-6">
      <div>
        <h1 className="text-2xl font-semibold">Identity</h1>
        <p className="text-muted-foreground text-sm">
          Verified domains anchor SSO routing and provisioning. Only one organization may verify a
          given domain.
        </p>
      </div>

      <section className="space-y-3">
        <h2 className="text-lg font-medium">Domains</h2>
        <ul className="space-y-2">
          {(domainsQ.data?.data ?? []).map((d) => (
            <li key={d.id} className="rounded-md border p-3">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <span className="font-mono">{d.domain}</span>
                  <span
                    className={`ml-2 rounded px-2 py-0.5 text-xs ${
                      d.status === "verified"
                        ? "bg-green-100 text-green-800"
                        : "bg-amber-100 text-amber-800"
                    }`}
                  >
                    {d.status}
                  </span>
                </div>
                {d.status !== "verified" && (
                  <Button size="sm" variant="outline" onClick={() => verifyDomain.mutate(d.id)}>
                    Verify
                  </Button>
                )}
              </div>
              {d.status !== "verified" && (
                <p className="text-muted-foreground mt-2 text-xs">
                  Add a TXT record at{" "}
                  <span className="font-mono">_openskill-verify.{d.domain}</span> with value{" "}
                  <span className="font-mono">{d.verification_token}</span>
                </p>
              )}
            </li>
          ))}
        </ul>
        <div className="flex items-end gap-2">
          <Input
            aria-label="New domain"
            className="max-w-xs"
            placeholder="school.example.edu"
            value={newDomain}
            onChange={(e) => setNewDomain(e.target.value)}
          />
          <Button
            disabled={!newDomain || claimDomain.isPending}
            onClick={() => claimDomain.mutate()}
          >
            Claim domain
          </Button>
        </div>
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-medium">SSO connections</h2>
        <ul className="space-y-2">
          {(ssoQ.data?.data ?? []).map((s) => (
            <li
              key={s.id}
              className="flex flex-wrap items-center justify-between gap-2 rounded-md border p-3"
            >
              <div>
                <span className="font-medium uppercase">{s.protocol}</span>{" "}
                <span className="font-mono text-xs">{s.oidc_issuer}</span>
                <span className="ml-2 rounded bg-gray-100 px-2 py-0.5 text-xs">{s.status}</span>
                {s.enforce_sso && (
                  <span className="ml-2 rounded bg-blue-100 px-2 py-0.5 text-xs text-blue-800">
                    enforced
                  </span>
                )}
                {s.allow_jit && (
                  <span className="text-muted-foreground ml-2 text-xs">JIT: {s.default_role}</span>
                )}
              </div>
              <div className="flex gap-2">
                {s.status !== "active" ? (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => patchSso.mutate({ id: s.id, body: { status: "active" } })}
                  >
                    Activate
                  </Button>
                ) : (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() =>
                      patchSso.mutate({ id: s.id, body: { enforce_sso: !s.enforce_sso } })
                    }
                  >
                    {s.enforce_sso ? "Stop enforcing" : "Enforce SSO"}
                  </Button>
                )}
              </div>
            </li>
          ))}
        </ul>
        <div className="flex flex-wrap items-end gap-2">
          <Input
            aria-label="OIDC issuer"
            className="max-w-xs"
            placeholder="https://login.idp.example.com"
            value={issuer}
            onChange={(e) => setIssuer(e.target.value)}
          />
          <Input
            aria-label="Client ID"
            className="max-w-[10rem]"
            placeholder="client id"
            value={clientId}
            onChange={(e) => setClientId(e.target.value)}
          />
          <Input
            aria-label="Client secret"
            className="max-w-[10rem]"
            type="password"
            placeholder="client secret"
            value={clientSecret}
            onChange={(e) => setClientSecret(e.target.value)}
          />
          <label className="flex items-center gap-1 text-sm">
            <input
              aria-label="Allow JIT"
              type="checkbox"
              checked={allowJit}
              onChange={(e) => setAllowJit(e.target.checked)}
            />
            JIT provisioning
          </label>
          <Button
            disabled={!issuer || !clientId || createSso.isPending}
            onClick={() => createSso.mutate()}
          >
            Add OIDC
          </Button>
        </div>
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-medium">SCIM provisioning tokens</h2>
        {mintedToken && (
          <div className="rounded-md border border-amber-300 bg-amber-50 p-3 text-sm">
            Copy this token now — it will not be shown again:
            <div className="mt-1 break-all font-mono text-xs">{mintedToken}</div>
          </div>
        )}
        <ul className="space-y-2">
          {(tokensQ.data?.data ?? []).map((t) => (
            <li key={t.id} className="flex items-center justify-between rounded-md border p-3">
              <div>
                <span className="font-medium">{t.name}</span>
                {t.revoked_at ? (
                  <span className="ml-2 text-xs text-red-700">revoked</span>
                ) : (
                  <span className="text-muted-foreground ml-2 text-xs">
                    last used: {t.last_used_at ?? "never"}
                  </span>
                )}
              </div>
              {!t.revoked_at && (
                <Button size="sm" variant="destructive" onClick={() => revokeToken.mutate(t.id)}>
                  Revoke
                </Button>
              )}
            </li>
          ))}
        </ul>
        <div className="flex items-end gap-2">
          <Input
            aria-label="Token name"
            className="max-w-xs"
            placeholder="Entra ID"
            value={tokenName}
            onChange={(e) => setTokenName(e.target.value)}
          />
          <Button disabled={!tokenName || mintToken.isPending} onClick={() => mintToken.mutate()}>
            Mint token
          </Button>
        </div>
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-medium">Identity queue</h2>
        <p className="text-muted-foreground text-sm">
          Ambiguous external identities wait here — link to an existing member or reject. Nothing is
          guessed automatically.
        </p>
        <ul className="space-y-2">
          {(queueQ.data?.data ?? []).map((q) => (
            <li key={q.id} className="rounded-md border p-3">
              <div className="text-sm">
                <span className="font-mono text-xs">{q.subject}</span>
                {q.email && <span className="ml-2">{q.email}</span>}
                <span className="text-muted-foreground ml-2 text-xs">
                  {q.source} · {q.reason}
                </span>
              </div>
              <div className="mt-2 flex items-center gap-2">
                <Input
                  aria-label={`Link user id for ${q.subject}`}
                  className="max-w-[16rem]"
                  placeholder="user id to link"
                  value={linkUserId}
                  onChange={(e) => setLinkUserId(e.target.value)}
                />
                <Button
                  size="sm"
                  disabled={!linkUserId}
                  onClick={() =>
                    resolveQueue.mutate({ id: q.id, action: "link", user_id: linkUserId })
                  }
                >
                  Link
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => resolveQueue.mutate({ id: q.id, action: "reject" })}
                >
                  Reject
                </Button>
              </div>
            </li>
          ))}
          {(queueQ.data?.data ?? []).length === 0 && (
            <li className="text-muted-foreground text-sm">Queue is empty.</li>
          )}
        </ul>
      </section>
    </div>
  );
}

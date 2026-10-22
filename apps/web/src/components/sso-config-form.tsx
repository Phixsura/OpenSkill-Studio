"use client";

import { useState } from "react";

const PROVIDERS = [
  { value: "oidc", label: "OpenID Connect" },
  { value: "saml", label: "SAML 2.0" },
  { value: "google", label: "Google Workspace" },
  { value: "azure_ad", label: "Azure AD" },
  { value: "okta", label: "Okta" },
];

interface SsoConfigFormProps { onSave: (config: { provider: string; clientId: string; issuerUrl: string }) => void; }

export function SsoConfigForm({ onSave }: SsoConfigFormProps) {
  const [provider, setProvider] = useState("oidc");
  const [clientId, setClientId] = useState("");
  const [issuerUrl, setIssuerUrl] = useState("");

  return (
    <div className="rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <h3 className="font-semibold">SSO Configuration</h3>
      <div className="mt-3 space-y-3">
        <select value={provider} onChange={e => setProvider(e.target.value)}
          className="w-full rounded border p-2 text-sm dark:border-gray-600 dark:bg-gray-700">
          {PROVIDERS.map(p => <option key={p.value} value={p.value}>{p.label}</option>)}
        </select>
        <input value={clientId} onChange={e => setClientId(e.target.value)} placeholder="Client ID"
          className="w-full rounded border p-2 text-sm dark:border-gray-600 dark:bg-gray-700" />
        <input value={issuerUrl} onChange={e => setIssuerUrl(e.target.value)} placeholder="Issuer URL"
          className="w-full rounded border p-2 text-sm dark:border-gray-600 dark:bg-gray-700" />
      </div>
      <button onClick={() => onSave({ provider, clientId, issuerUrl })} disabled={!clientId || !issuerUrl}
        className="mt-3 rounded bg-blue-600 px-4 py-2 text-sm text-white disabled:opacity-50">Save SSO Config</button>
    </div>
  );
}

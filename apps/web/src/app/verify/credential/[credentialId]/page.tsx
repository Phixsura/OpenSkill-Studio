"use client";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

interface CredentialVerification {
  credential_type: string;
  status: string;
  is_valid: boolean;
  issued_at: string | null;
  expires_at: string | null;
  capability_name: string | null;
  verification_timestamp: string;
}

export default function VerifyCredentialPage() {
  const { credentialId } = useParams<{ credentialId: string }>();
  const { data, isLoading, error, isError } = useQuery({
    queryKey: ["verify-credential", credentialId],
    queryFn: () => api<{ data: CredentialVerification }>(`/verify/credential/${credentialId}`),
    enabled: !!credentialId,
    retry: false,
  });

  if (isLoading)
    if (isError) return <div className="p-8 text-center text-red-600">Failed to load data</div>;

  return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-[hsl(var(--muted-foreground))]">Verifying credential…</div>
      </div>
    );

  if (error || !data?.data)
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="mx-4 max-w-md rounded-lg border bg-[hsl(var(--card))] p-8 text-center shadow-sm">
          <div className="mb-4 text-4xl">🚫</div>
          <h1 className="mb-2 text-xl font-bold">Credential Not Found</h1>
          <p className="text-[hsl(var(--muted-foreground))]">
            This credential may have been revoked or does not exist.
          </p>
        </div>
      </div>
    );

  const cred = data.data;
  return (
    <div className="min-h-screen bg-[hsl(var(--background))]">
      <div className="mx-auto max-w-2xl px-4 py-12">
        <div className="rounded-lg border bg-[hsl(var(--card))] p-8 shadow-sm">
          <div className="mb-6 flex items-center justify-between">
            <h1 className="text-2xl font-bold">Credential Verification</h1>
            <span
              className={`rounded-full px-3 py-1 text-sm font-medium ${cred.is_valid ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}
            >
              {cred.is_valid ? "✓ Valid" : "✗ Invalid"}
            </span>
          </div>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-[hsl(var(--muted-foreground))]">Credential Type</p>
              <p className="font-medium">{cred.credential_type}</p>
            </div>
            {cred.capability_name && (
              <div>
                <p className="text-sm text-[hsl(var(--muted-foreground))]">Capability</p>
                <p className="font-medium">{cred.capability_name}</p>
              </div>
            )}
            <div>
              <p className="text-sm text-[hsl(var(--muted-foreground))]">Status</p>
              <p className="font-medium capitalize">{cred.status}</p>
            </div>
            {cred.issued_at && (
              <div>
                <p className="text-sm text-[hsl(var(--muted-foreground))]">Issued</p>
                <p className="font-medium">{new Date(cred.issued_at).toLocaleDateString()}</p>
              </div>
            )}
            {cred.expires_at && (
              <div>
                <p className="text-sm text-[hsl(var(--muted-foreground))]">Expires</p>
                <p className="font-medium">{new Date(cred.expires_at).toLocaleDateString()}</p>
              </div>
            )}
          </div>
          <p className="mt-8 text-center text-xs text-[hsl(var(--muted-foreground))]">
            Verified by OpenSkill Studio at {new Date(cred.verification_timestamp).toLocaleString()}
          </p>
        </div>
      </div>
    </div>
  );
}

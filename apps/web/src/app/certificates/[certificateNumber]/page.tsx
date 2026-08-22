"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";

import { api, ApiError } from "@/lib/api";

interface Certificate {
  certificate_number: string;
  user_name: string;
  path_name: string;
  org_name: string;
  issued_at: string;
  skills_completed: number;
}

export default function CertificateVerificationPage() {
  const { certificateNumber } = useParams<{ certificateNumber: string }>();

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["certificate", certificateNumber],
    queryFn: () =>
      api<{ data: Certificate }>(`/certificates/${certificateNumber}`),
  });

  const cert = data?.data;

  const is404 = error instanceof ApiError && error.status === 404;

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[hsl(var(--background))]">
        <p className="text-[hsl(var(--muted-foreground))]">Verifying certificate...</p>
      </div>
    );
  }

  if (isError || !cert) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[hsl(var(--background))]">
        <div className="mx-auto max-w-md text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-red-100 dark:bg-red-950">
            <svg className="h-8 w-8 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold">
            {is404 ? "Certificate Not Found" : "Unable to Verify"}
          </h1>
          <p className="mt-2 text-[hsl(var(--muted-foreground))]">
            {is404
              ? "The certificate number provided could not be verified. Please check the number and try again."
              : "We were unable to verify this certificate at the moment. Please try again later."}
          </p>
          <Link
            href="/"
            className="mt-4 inline-block text-sm text-[hsl(var(--primary))] hover:underline"
          >
            Go to homepage
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[hsl(var(--background))] p-4">
      <div className="w-full max-w-lg">
        {/* Verification card */}
        <div className="overflow-hidden rounded-xl border-2 border-green-200 bg-[hsl(var(--card))] shadow-lg dark:border-green-800">
          {/* Verified badge header */}
          <div className="bg-green-50 px-6 py-4 dark:bg-green-950">
            <div className="flex items-center justify-center gap-2">
              <svg className="h-6 w-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-lg font-semibold text-green-700 dark:text-green-300">
                Verified Certificate
              </span>
            </div>
          </div>

          {/* Certificate details */}
          <div className="space-y-4 p-6">
            <div className="text-center">
              <p className="text-sm uppercase tracking-wide text-[hsl(var(--muted-foreground))]">
                This certifies that
              </p>
              <h2 className="mt-1 text-2xl font-bold">{cert.user_name}</h2>
            </div>

            <div className="text-center">
              <p className="text-sm uppercase tracking-wide text-[hsl(var(--muted-foreground))]">
                has successfully completed
              </p>
              <h3 className="mt-1 text-xl font-semibold text-[hsl(var(--primary))]">
                {cert.path_name}
              </h3>
            </div>

            <div className="flex justify-center">
              <div className="rounded-lg bg-[hsl(var(--secondary))] px-4 py-2 text-center">
                <p className="text-xs text-[hsl(var(--muted-foreground))]">Organization</p>
                <p className="font-medium">{cert.org_name}</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 text-center">
              <div>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">Issue Date</p>
                <p className="font-medium">
                  {new Date(cert.issued_at).toLocaleDateString(undefined, {
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                  })}
                </p>
              </div>
              <div>
                <p className="text-xs text-[hsl(var(--muted-foreground))]">Skills Completed</p>
                <p className="font-medium">{cert.skills_completed}</p>
              </div>
            </div>

            <div className="rounded-md bg-[hsl(var(--secondary))] px-4 py-2 text-center">
              <p className="text-xs text-[hsl(var(--muted-foreground))]">Certificate Number</p>
              <p className="font-mono text-sm font-medium">{cert.certificate_number}</p>
            </div>
          </div>

          {/* Footer */}
          <div className="border-t px-6 py-3 text-center">
            <p className="text-xs text-[hsl(var(--muted-foreground))]">
              Verified by OpenSkill Studio
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

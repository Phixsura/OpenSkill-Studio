import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

vi.mock("next/navigation", () => ({
  useParams: () => ({ certificateNumber: "abc-123-def-456" }),
}));

const { MockApiError } = vi.hoisted(() => {
  class MockApiError extends Error {
    status: number;
    constructor(message: string, status: number) {
      super(message);
      this.status = status;
    }
  }
  return { MockApiError };
});

vi.mock("@/lib/api", () => ({
  api: vi.fn(),
  ApiError: MockApiError,
}));

import CertificateVerificationPage from "@/app/certificates/[certificateNumber]/page";
import { api } from "@/lib/api";

const mockApi = vi.mocked(api);

function createWrapper() {
  const qc = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={qc}>{children}</QueryClientProvider>
  );
}

describe("CertificateVerificationPage", () => {
  beforeEach(() => vi.clearAllMocks());

  it("shows loading state", () => {
    mockApi.mockReturnValue(new Promise(() => {}));
    render(<CertificateVerificationPage />, { wrapper: createWrapper() });
    expect(screen.getByText("Verifying certificate...")).toBeDefined();
  });

  it("shows not found state on error", async () => {
    mockApi.mockRejectedValue(new MockApiError("not found", 404));
    render(<CertificateVerificationPage />, { wrapper: createWrapper() });
    expect(await screen.findByText("Certificate Not Found")).toBeDefined();
    expect(
      screen.getByText(/could not be verified/),
    ).toBeDefined();
    expect(screen.getByText("Go to homepage")).toBeDefined();
  });

  it("renders verified certificate details", async () => {
    mockApi.mockResolvedValue({
      data: {
        certificate_number: "abc-123-def-456",
        user_name: "Alice Johnson",
        path_name: "Full-Stack Bootcamp",
        org_name: "TechCorp",
        issued_at: "2026-07-15T10:30:00Z",
        skills_completed: 12,
      },
    });
    render(<CertificateVerificationPage />, { wrapper: createWrapper() });

    expect(await screen.findByText("Verified Certificate")).toBeDefined();
    expect(screen.getByText("Alice Johnson")).toBeDefined();
    expect(screen.getByText("Full-Stack Bootcamp")).toBeDefined();
    expect(screen.getByText("TechCorp")).toBeDefined();
    expect(screen.getByText("12")).toBeDefined();
    expect(screen.getByText("abc-123-def-456")).toBeDefined();
  });

  it("links homepage in not-found state", async () => {
    mockApi.mockRejectedValue(new MockApiError("not found", 404));
    render(<CertificateVerificationPage />, { wrapper: createWrapper() });
    const link = await screen.findByText("Go to homepage");
    expect(link.closest("a")?.getAttribute("href")).toBe("/");
  });
});

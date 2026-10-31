import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useParams: () => ({ orgId: "org-1", installationId: "inst-1" }),
  useRouter: () => ({ push: vi.fn(), back: vi.fn() }),
}));

vi.mock("@/lib/api", () => ({
  apiWithAuth: { get: vi.fn().mockResolvedValue({ data: { data: {
    id: "inst-1", app_id: "app-1", org_id: "org-1", status: "active",
  } } }) },
}));

import OrgAppInstallationPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/apps/[installationId]/page";

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={qc}>{children}</QueryClientProvider>
  );
}

describe("OrgAppInstallationPage", () => {
  it("renders without crashing", () => {
    const { container } = render(<OrgAppInstallationPage />, { wrapper: makeWrapper() });
    expect(container).toBeTruthy();
  });

  it("has page content", () => {
    const { container } = render(<OrgAppInstallationPage />, { wrapper: makeWrapper() });
    expect(container.querySelectorAll("div").length).toBeGreaterThan(0);
  });
});

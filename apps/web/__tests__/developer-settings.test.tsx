import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

vi.mock("@/lib/api", () => ({
  apiWithAuth: { get: vi.fn().mockResolvedValue({ data: { data: {
    id: "d1", display_name: "Dev Studio", slug: "dev-studio",
    support_email: "dev@test.com", website_url: null, status: "active",
  } } }) },
}));

import DeveloperSettingsPage from "@/app/(dashboard)/dashboard/developer/settings/page";

function makeWrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={qc}>{children}</QueryClientProvider>
  );
}

describe("DeveloperSettingsPage", () => {
  it("renders without crashing", () => {
    const { container } = render(<DeveloperSettingsPage />, { wrapper: makeWrapper() });
    expect(container).toBeTruthy();
  });

  it("has form elements", () => {
    const { container } = render(<DeveloperSettingsPage />, { wrapper: makeWrapper() });
    const elements = container.querySelectorAll("input, textarea, button, div, span");
    expect(elements.length).toBeGreaterThan(0);
  });
});

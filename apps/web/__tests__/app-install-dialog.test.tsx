import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import { AppInstallDialog } from "@/components/app-install-dialog";

const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
function Wrapper({ children }: { children: ReactNode }) {
  return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
}

describe("AppInstallDialog", () => {
  const BASE = {
    appId: "app-1",
    appName: "Test App",
    orgId: "org-1",
    permissions: ["read:cohorts", "write:projects"],
    onClose: vi.fn(),
  };

  it("renders app name", () => {
    const { container } = render(<AppInstallDialog {...BASE} />, { wrapper: Wrapper });
    expect(container.textContent).toContain("Test App");
  });

  it("renders permissions", () => {
    const { container } = render(<AppInstallDialog {...BASE} />, { wrapper: Wrapper });
    expect(container.textContent).toContain("read:cohorts");
  });

  it("renders install button", () => {
    const { container } = render(<AppInstallDialog {...BASE} />, { wrapper: Wrapper });
    const btn = container.querySelector("button");
    expect(btn).toBeTruthy();
  });
});

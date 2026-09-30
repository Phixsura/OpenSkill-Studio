import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard/ecosystem/components",
  useRouter: () => ({ replace: vi.fn(), push: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
}));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import ComponentsPage from "@/app/(dashboard)/dashboard/ecosystem/components/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

const NODE = "N".repeat(26);

beforeEach(() => {
  vi.clearAllMocks();
  api.mockImplementation((path: string) => {
    if (path.startsWith("/ecosystem/graph/node/"))
      return Promise.resolve({
        data: {
          depends_on: [
            {
              id: "E1".padEnd(26, "e"),
              from_kind: "workflow_pack",
              from_id: NODE,
              to_kind: "model_version",
              to_id: "DEP1".padEnd(26, "x"),
              constraint_type: "uses",
            },
          ],
          dependents: [
            {
              id: "E2".padEnd(26, "f"),
              from_kind: "learning_path",
              from_id: "PARENT01".padEnd(26, "y"),
              to_kind: "workflow_pack",
              to_id: NODE,
              constraint_type: "requires",
            },
          ],
        },
      });
    return Promise.resolve({ data: [] });
  });
});

describe("Dependency graph inspector (ADR-016 §20 UI)", () => {
  it("Inspect node GETs the typed node path and renders both directions", async () => {
    render(<ComponentsPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByText("Graph"));
    fireEvent.change(screen.getByLabelText("Filter"), {
      target: { value: "workflow_pack" },
    });
    fireEvent.change(screen.getByPlaceholderText("node id"), { target: { value: NODE } });
    fireEvent.click(screen.getByText("Inspect node"));
    // Query fired with kind + id in the path
    expect(await screen.findByLabelText("Dependency graph")).toBeDefined();
    expect(api.mock.calls.some((c) => c[0] === `/ecosystem/graph/node/workflow_pack/${NODE}`)).toBe(
      true,
    );
    // Both directions rendered (truncated labels)
    expect(screen.getAllByText(/model_version:DEP1/).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/learning_path:PARENT01/).length).toBeGreaterThan(0);
  });

  it("Inspect is a no-op without a node id (no stray request)", async () => {
    render(<ComponentsPage />, { wrapper: wrapper() });
    fireEvent.click(await screen.findByText("Graph"));
    fireEvent.click(screen.getByText("Inspect node"));
    await new Promise((r) => setTimeout(r, 0));
    expect(
      api.mock.calls.some(
        (c) => typeof c[0] === "string" && (c[0] as string).startsWith("/ecosystem/graph/node/"),
      ),
    ).toBe(false);
  });
});

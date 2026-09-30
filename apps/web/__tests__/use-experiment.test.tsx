import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import { apiWithAuth } from "@/lib/api";
import { useExperiment } from "@/lib/useExperiment";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

let hookValue: ReturnType<typeof useExperiment>;

function Probe({ k }: { k: string }) {
  hookValue = useExperiment(k);
  return <div>{hookValue.variantKey ?? "default"}</div>;
}

beforeEach(() => vi.clearAllMocks());

describe("useExperiment (ADR-017 §7 self-serve hook)", () => {
  it("resolves the variant and exposes config; exposure posts the key", async () => {
    api.mockResolvedValue({
      data: { variant_key: "treatment", config: { sort: "quality" }, assigned_version: 1 },
    });
    render(<Probe k="surface-registry-sort" />, { wrapper: wrapper() });
    expect(await screen.findByText("treatment")).toBeTruthy();
    expect(api).toHaveBeenCalledWith(
      "/experiments/self/resolve",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ experiment_key: "surface-registry-sort" }),
      }),
    );
    expect(hookValue.config).toEqual({ sort: "quality" });
    act(() => hookValue.recordExposure("day-1"));
    await waitFor(() =>
      expect(api).toHaveBeenCalledWith(
        "/experiments/self/exposures",
        expect.objectContaining({
          body: JSON.stringify({
            experiment_key: "surface-registry-sort",
            dedup_key: "day-1",
          }),
        }),
      ),
    );
  });

  it("null variant renders the default experience", async () => {
    api.mockResolvedValue({ data: { variant_key: null, config: {} } });
    render(<Probe k="surface-unknown" />, { wrapper: wrapper() });
    expect(await screen.findByText("default")).toBeTruthy();
    expect(hookValue.config).toEqual({});
  });
});

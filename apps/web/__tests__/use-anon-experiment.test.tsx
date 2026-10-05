import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/lib/api", () => ({
  api: vi.fn(),
  apiWithAuth: vi.fn(),
  ApiError: class extends Error {},
}));

import { api, apiWithAuth } from "@/lib/api";
import { claimAnonymousId, getAnonymousId, useAnonExperiment } from "@/lib/useAnonExperiment";

const anonApi = vi.mocked(api);
const authedApi = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

let hookValue: ReturnType<typeof useAnonExperiment>;

function Probe({ k }: { k: string }) {
  hookValue = useAnonExperiment(k);
  return <div>{hookValue.variantKey ?? "default"}</div>;
}

beforeEach(() => {
  vi.clearAllMocks();
  window.localStorage.clear();
});

describe("useAnonExperiment (ADR-017 §4.17 pre-login hook)", () => {
  it("mints a 26-char no-colon device id once and keeps it", () => {
    const first = getAnonymousId();
    expect(first).toBeTruthy();
    expect(first).toHaveLength(26);
    expect(first).not.toContain(":");
    expect(getAnonymousId()).toBe(first); // sticky per device
  });

  it("resolves through the anon surface and records exposures with the id", async () => {
    anonApi.mockResolvedValue({
      data: { variant_key: "treatment", config: { cta: "big" } },
    });
    render(<Probe k="landing-cta" />, { wrapper: wrapper() });
    expect(await screen.findByText("treatment")).toBeTruthy();
    const anonymousId = getAnonymousId();
    expect(anonApi).toHaveBeenCalledWith(
      "/experiments/anon/resolve",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          experiment_key: "landing-cta",
          anonymous_id: anonymousId,
        }),
      }),
    );
    expect(hookValue.config).toEqual({ cta: "big" });
    act(() => hookValue.recordExposure("seen-1"));
    await waitFor(() =>
      expect(anonApi).toHaveBeenCalledWith(
        "/experiments/anon/exposures",
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({
            experiment_key: "landing-cta",
            anonymous_id: anonymousId,
            dedup_key: "seen-1",
          }),
        }),
      ),
    );
  });

  it("fails safe to the default experience on a broken response", async () => {
    anonApi.mockResolvedValue({ data: null } as never);
    render(<Probe k="landing-cta" />, { wrapper: wrapper() });
    expect(await screen.findByText("default")).toBeTruthy();
    expect(hookValue.config).toEqual({});
  });

  it("fails safe on a REJECTED request too (429/network — round 266)", async () => {
    // production fails rate limiting CLOSED on a Redis outage: the hook
    // must degrade to the default experience, never crash the page
    anonApi.mockRejectedValue(new Error("429"));
    render(<Probe k="landing-cta" />, { wrapper: wrapper() });
    expect(await screen.findByText("default")).toBeTruthy();
    expect(hookValue.config).toEqual({});
  });

  it("claimAnonymousId posts the device id to the link endpoint", async () => {
    getAnonymousId(); // mint
    authedApi.mockResolvedValue({ data: { migrated: 1, conflicts: 0 } });
    expect(await claimAnonymousId()).toBe(true);
    expect(authedApi).toHaveBeenCalledWith(
      "/experiments/self/identity-link",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ anonymous_id: getAnonymousId() }),
      }),
    );
  });

  it("claimAnonymousId fails safe on a 422 (shared-device rebinding)", async () => {
    getAnonymousId();
    authedApi.mockRejectedValue(new Error("422"));
    expect(await claimAnonymousId()).toBe(false); // login proceeds regardless
  });
});

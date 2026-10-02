import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard/experiments/new",
  useRouter: () => ({ replace: vi.fn(), push: vi.fn() }),
}));
vi.mock("@/lib/use-me", () => ({ usePlatformAdmin: () => true }));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import NewExperimentPage from "@/app/(dashboard)/dashboard/experiments/new/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

beforeEach(() => {
  vi.clearAllMocks();
  api.mockResolvedValue({ data: [] });
});

describe("Experiment builder design fields (v2 round 10)", () => {
  it("hides switchback inputs for parallel and reveals them for switchback", () => {
    render(<NewExperimentPage />, { wrapper: wrapper() });
    expect(screen.queryByLabelText("Switch window (minutes)")).toBeNull();
    fireEvent.change(screen.getByLabelText("Design"), {
      target: { value: "switchback" },
    });
    expect(screen.getByLabelText("Switch window (minutes)")).toBeTruthy();
    expect(screen.getByLabelText("Washout (minutes)")).toBeTruthy();
  });

  it("submits design, allocation and the switchback config in the spec", async () => {
    api.mockImplementation(async (path: string) => {
      if (path === "/experiments") return { data: { id: "E".repeat(26) } };
      return { data: [] };
    });
    render(<NewExperimentPage />, { wrapper: wrapper() });
    fireEvent.change(screen.getByLabelText("Design"), {
      target: { value: "switchback" },
    });
    fireEvent.change(screen.getByLabelText("Allocation"), {
      target: { value: "bandit" },
    });
    fireEvent.change(screen.getByLabelText("Switch window (minutes)"), {
      target: { value: "60" },
    });
    fireEvent.change(screen.getByLabelText("Washout (minutes)"), {
      target: { value: "10" },
    });
    fireEvent.change(screen.getByLabelText("Hypothesis"), {
      target: { value: "switchback hypothesis long enough" },
    });
    fireEvent.click(screen.getByText(/Create experiment/));
    await waitFor(() =>
      expect(api).toHaveBeenCalledWith(
        `/experiments/${"E".repeat(26)}/versions`,
        expect.objectContaining({ method: "POST" }),
      ),
    );
    const call = api.mock.calls.find((c) => String(c[0]).endsWith("/versions"));
    const body = JSON.parse(String(call?.[1]?.body));
    expect(body.spec.design).toBe("switchback");
    expect(body.spec.allocation_mode).toBe("bandit");
    expect(body.spec.switchback).toEqual({
      switch_unit: "platform_window",
      window_minutes: 60,
      washout_minutes: 10,
    });
  });
});

describe("Segment opt-in (v2 §4.8)", () => {
  it("adds segments:[org] to the spec when checked (user units only)", async () => {
    api.mockImplementation(async (path: string) => {
      if (path === "/experiments") return { data: { id: "E".repeat(26) } };
      return { data: [] };
    });
    render(<NewExperimentPage />, { wrapper: wrapper() });
    fireEvent.click(screen.getByLabelText("Org segment breakdown"));
    fireEvent.change(screen.getByLabelText("Hypothesis"), {
      target: { value: "segment opt-in rides the spec" },
    });
    fireEvent.click(screen.getByText(/Create experiment/));
    await waitFor(() =>
      expect(api.mock.calls.some((c) => String(c[0]).endsWith("/versions"))).toBe(true),
    );
    const call = api.mock.calls.find((c) => String(c[0]).endsWith("/versions"));
    const body = JSON.parse(String(call?.[1]?.body));
    expect(body.spec.segments).toEqual(["org"]);
  });

  it("sends power.mde when the MDE field is filled and omits it when blank", async () => {
    api.mockImplementation(async (path: string) => {
      if (path === "/experiments") return { data: { id: "E".repeat(26) } };
      return { data: [] };
    });
    render(<NewExperimentPage />, { wrapper: wrapper() });
    fireEvent.change(screen.getByLabelText(/Power target/), {
      target: { value: "20" },
    });
    fireEvent.change(screen.getByLabelText("Hypothesis"), {
      target: { value: "power target rides the spec" },
    });
    fireEvent.click(screen.getByText(/Create experiment/));
    await waitFor(() =>
      expect(api.mock.calls.some((c) => String(c[0]).endsWith("/versions"))).toBe(true),
    );
    const call = api.mock.calls.find((c) => String(c[0]).endsWith("/versions"));
    const body = JSON.parse(String(call?.[1]?.body));
    expect(body.spec.power).toEqual({ mde: 0.2 });
  });

  it("omits power entirely when the MDE field is blank", async () => {
    api.mockImplementation(async (path: string) => {
      if (path === "/experiments") return { data: { id: "E".repeat(26) } };
      return { data: [] };
    });
    render(<NewExperimentPage />, { wrapper: wrapper() });
    fireEvent.change(screen.getByLabelText("Hypothesis"), {
      target: { value: "no power target means no block" },
    });
    fireEvent.click(screen.getByText(/Create experiment/));
    await waitFor(() =>
      expect(api.mock.calls.some((c) => String(c[0]).endsWith("/versions"))).toBe(true),
    );
    const call = api.mock.calls.find((c) => String(c[0]).endsWith("/versions"));
    const body = JSON.parse(String(call?.[1]?.body));
    expect(body.spec.power).toBeUndefined();
  });
});

import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { HealthProbePanel } from "@/components/health-probe-panel";

const mockProbes = [
  { probeType: "liveness" as const, healthy: true, checks: 500, lastLatencyMs: 5 },
  { probeType: "readiness" as const, healthy: true, checks: 500, lastLatencyMs: 12 },
  { probeType: "startup" as const, healthy: false, checks: 3, lastMessage: "Waiting for DB" },
];

describe("HealthProbePanel", () => {
  it("renders probes with status", () => {
    const { container } = render(<HealthProbePanel probes={mockProbes} />);
    expect(container.textContent).toContain("liveness");
    expect(container.textContent).toContain("readiness");
    expect(container.textContent).toContain("startup");
    expect(container.textContent).toContain("Degraded");
  });

  it("shows check counts", () => {
    const { container } = render(<HealthProbePanel probes={mockProbes} />);
    expect(container.textContent).toContain("500 checks");
    expect(container.textContent).toContain("5ms");
  });

  it("shows unhealthy message", () => {
    const { container } = render(<HealthProbePanel probes={mockProbes} />);
    expect(container.textContent).toContain("Waiting for DB");
  });

  it("calls onCheck", () => {
    const onCheck = vi.fn();
    const { getAllByText } = render(<HealthProbePanel probes={mockProbes} onCheck={onCheck} />);
    fireEvent.click(getAllByText("Check")[0]);
    expect(onCheck).toHaveBeenCalledWith("liveness");
  });
});

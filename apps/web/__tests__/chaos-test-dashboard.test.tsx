import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ChaosTestDashboard } from "@/components/chaos-test-dashboard";

describe("ChaosTestDashboard", () => {
  const result = { resilience_score: 80, grade: "A", error_spike_pct: 1.9,
    latency_spike_ms: 200, recovery_time_sec: 15, fully_recovered: true };
  it("renders", () => {
    const { container } = render(
      <ChaosTestDashboard experimentName="Latency test" faultType="latency" result={result} onRerun={vi.fn()} />
    );
    expect(container.textContent).toContain("Chaos Test Results");
    expect(container.textContent).toContain("A");
    expect(container.textContent).toContain("80");
    expect(container.textContent).toContain("Fully recovered");
  });
  it("rerun", () => {
    const fn = vi.fn();
    const { container } = render(
      <ChaosTestDashboard experimentName="Test" faultType="latency" result={result} onRerun={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Re-run Test")!);
    expect(fn).toHaveBeenCalled();
  });
});

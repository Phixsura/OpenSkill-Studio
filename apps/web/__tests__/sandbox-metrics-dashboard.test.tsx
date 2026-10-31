import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SandboxMetricsDashboard } from "@/components/sandbox-metrics-dashboard";

const mockMetrics = {
  extensionId: "ext-1", executions: 15420, avgCpuMs: 85,
  avgMemoryMb: 128, peakMemoryMb: 220, memoryLimitMb: 256,
  totalIoOps: 45000, successRate: 99.2, avgDurationMs: 145,
  quotaUsedPercent: 72,
};

describe("SandboxMetricsDashboard", () => {
  it("renders all metric tiles", () => {
    const { container } = render(<SandboxMetricsDashboard metrics={mockMetrics} />);
    expect(container.textContent).toContain("Sandbox Metrics");
    expect(container.textContent).toContain("15,420");
    expect(container.textContent).toContain("99.2%");
    expect(container.textContent).toContain("145ms");
    expect(container.textContent).toContain("45,000");
  });

  it("renders memory gauge", () => {
    const { container } = render(<SandboxMetricsDashboard metrics={mockMetrics} />);
    expect(container.textContent).toContain("220/256MB");
    expect(container.textContent).toContain("Avg: 128MB");
  });

  it("renders quota bar", () => {
    const { container } = render(<SandboxMetricsDashboard metrics={mockMetrics} />);
    expect(container.textContent).toContain("72%");
  });

  it("calls onViewLogs", () => {
    const onView = vi.fn();
    const { getByText } = render(<SandboxMetricsDashboard metrics={mockMetrics} onViewLogs={onView} />);
    fireEvent.click(getByText("📋 View Logs"));
    expect(onView).toHaveBeenCalled();
  });
});

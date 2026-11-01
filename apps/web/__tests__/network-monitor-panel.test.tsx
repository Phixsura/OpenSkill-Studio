import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { NetworkMonitorPanel } from "@/components/network-monitor-panel";

const props = {
  totalRequests: 5000, errorRate: 3.5,
  bandwidth: { totalMb: 45.2, limitMb: 100, usagePercent: 45.2 },
  latency: { count: 5000, avg: 55, p50: 40, p95: 150, p99: 350, max: 1200 },
  topEndpoints: [
    { url: "https://api.example.com/data", count: 2500 },
    { url: "https://api.example.com/auth", count: 1000 },
  ],
  anomalies: [{ message: "High p95 latency: 5200ms" }],
};

describe("NetworkMonitorPanel", () => {
  it("renders stats", () => {
    const { container } = render(<NetworkMonitorPanel {...props} />);
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("3.5%");
    expect(container.textContent).toContain("45.2MB");
    expect(container.textContent).toContain("55ms");
  });

  it("shows latency percentiles", () => {
    const { container } = render(<NetworkMonitorPanel {...props} />);
    expect(container.textContent).toContain("p50");
    expect(container.textContent).toContain("40ms");
    expect(container.textContent).toContain("350ms");
  });

  it("shows top endpoints", () => {
    const { getByText, container } = render(<NetworkMonitorPanel {...props} />);
    fireEvent.click(getByText("Top Endpoints (2)"));
    expect(container.textContent).toContain("api.example.com/data");
    expect(container.textContent).toContain("2500");
  });

  it("shows anomalies", () => {
    const { getByText, container } = render(<NetworkMonitorPanel {...props} />);
    fireEvent.click(getByText("Anomalies (1)"));
    expect(container.textContent).toContain("High p95 latency");
  });
});

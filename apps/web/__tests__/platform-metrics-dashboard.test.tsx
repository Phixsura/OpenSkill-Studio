import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformMetricsDashboard } from "@/components/platform-metrics-dashboard";

describe("PlatformMetricsDashboard", () => {
  it("shows all metrics", () => {
    const { container } = render(<PlatformMetricsDashboard apps={100} developers={20} installations={500} activeUsers={150}
      executions24h={10000} errors24h={50} errorRate={0.5} webhooks24h={2000} healthStatus="healthy" avgHealth={97} />);
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("0.5%");
    expect(container.textContent).toContain("97%");
  });
  it("renders 8 cards", () => {
    const { container } = render(<PlatformMetricsDashboard apps={0} developers={0} installations={0} activeUsers={0}
      executions24h={0} errors24h={0} errorRate={0} webhooks24h={0} healthStatus="healthy" avgHealth={100} />);
    expect(container.querySelectorAll("[class*='rounded-lg']").length).toBe(8);
  });
});

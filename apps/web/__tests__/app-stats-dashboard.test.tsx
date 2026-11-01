import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppStatsDashboard } from "@/components/app-stats-dashboard";

const STATS = {
  total_installs: 100, active_installs: 80, total_executions: 5000,
  execution_success_rate: 99.5, total_webhooks: 2000, webhook_success_rate: 98.0,
  total_api_calls: 15000, error_count: 25,
};

describe("AppStatsDashboard", () => {
  it("renders all stat cards", () => {
    const { container } = render(<AppStatsDashboard stats={STATS} />);
    expect(container.querySelectorAll("[class*='rounded-lg']").length).toBeGreaterThanOrEqual(8);
  });

  it("shows active installs", () => {
    const { container } = render(<AppStatsDashboard stats={STATS} />);
    expect(container.textContent).toContain("80");
  });

  it("shows success rate", () => {
    const { container } = render(<AppStatsDashboard stats={STATS} />);
    expect(container.textContent).toContain("99.5%");
  });

  it("shows error count", () => {
    const { container } = render(<AppStatsDashboard stats={STATS} />);
    expect(container.textContent).toContain("25");
  });
});

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthAlertList } from "@/components/health-alert-list";

const ALERTS = [
  { rule: "high_error_rate", severity: "warning", metric: "error_rate_pct", value: 15, threshold: 10, message: "x" },
  { rule: "low_health_score", severity: "critical", metric: "score", value: 30, threshold: 50, message: "x" },
];

describe("HealthAlertList", () => {
  it("shows no alerts state", () => {
    const { container } = render(<HealthAlertList alerts={[]} />);
    expect(container.textContent).toContain("No active alerts");
  });

  it("shows alert rules", () => {
    const { container } = render(<HealthAlertList alerts={ALERTS} />);
    expect(container.textContent).toContain("high error rate");
    expect(container.textContent).toContain("low health score");
  });

  it("sorts critical first", () => {
    const { container } = render(<HealthAlertList alerts={ALERTS} />);
    const items = container.querySelectorAll("[class*='rounded-lg']");
    expect(items[0].textContent).toContain("low health score");
  });

  it("shows metric values", () => {
    const { container } = render(<HealthAlertList alerts={ALERTS} />);
    expect(container.textContent).toContain("15");
  });
});

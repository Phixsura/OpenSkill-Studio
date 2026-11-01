import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIUsageAlertCard from "../src/components/api-usage-alert-card";

const rules = [
  { rule_id: "r1", metric: "api_calls", condition: "exceeds", threshold: 10000, fired: true, fire_count: 3 },
  { rule_id: "r2", metric: "error_rate", condition: "spike", threshold: 50, fired: false, fire_count: 1 },
];

describe("APIUsageAlertCard", () => {
  it("renders header and firing count", () => {
    const { container } = render(<APIUsageAlertCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("Usage Alerts");
    expect(container.textContent).toContain("1 firing");
  });

  it("shows conditions and metrics", () => {
    const { container } = render(<APIUsageAlertCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("exceeds");
    expect(container.textContent).toContain("api_calls");
    expect(container.textContent).toContain("spike");
  });

  it("shows empty state", () => {
    const { container } = render(<APIUsageAlertCard rules={[]} appName="App" />);
    expect(container.textContent).toContain("No usage alerts");
  });
});

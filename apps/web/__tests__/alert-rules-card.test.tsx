import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import AlertRulesCard from "../src/components/alert-rules-card";

const rules = [
  {
    rule_id: "r1",
    name: "High CPU",
    metric: "cpu_pct",
    operator: "gt" as const,
    threshold: 90,
    state: "firing" as const,
    enabled: true,
  },
  {
    rule_id: "r2",
    name: "Low Disk",
    metric: "disk_free_gb",
    operator: "lt" as const,
    threshold: 10,
    state: "ok" as const,
    enabled: true,
  },
  {
    rule_id: "r3",
    name: "Error Rate",
    metric: "error_pct",
    operator: "gte" as const,
    threshold: 5,
    state: "ok" as const,
    enabled: false,
  },
];

describe("AlertRulesCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<AlertRulesCard rules={rules} appName="My App" />);
    expect(container.textContent).toContain("Alert Rules");
    expect(container.textContent).toContain("My App");
  });

  it("shows firing badge", () => {
    const { container } = render(<AlertRulesCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("1 firing");
  });

  it("shows all-clear when nothing firing", () => {
    const okRules = rules.map((r) => ({ ...r, state: "ok" as const }));
    const { container } = render(<AlertRulesCard rules={okRules} appName="App" />);
    expect(container.textContent).toContain("All clear");
  });

  it("renders rule names", () => {
    const { container } = render(<AlertRulesCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("High CPU");
    expect(container.textContent).toContain("Low Disk");
  });

  it("shows metric conditions with symbols", () => {
    const { container } = render(<AlertRulesCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("cpu_pct > 90");
    expect(container.textContent).toContain("disk_free_gb < 10");
  });

  it("shows state labels", () => {
    const { container } = render(<AlertRulesCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("Firing");
    expect(container.textContent).toContain("OK");
  });

  it("shows empty state", () => {
    const { container } = render(<AlertRulesCard rules={[]} appName="App" />);
    expect(container.textContent).toContain("No alert rules");
  });
});

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIThrottleRuleCard from "../src/components/api-throttle-rule-card";

const rules = [
  { rule_id: "r1", path_pattern: "/api/users/*", max_requests: 100, window_seconds: 60, enabled: true },
  { rule_id: "r2", path_pattern: "/api/search", max_requests: 10, window_seconds: 10, enabled: false },
];

describe("APIThrottleRuleCard", () => {
  it("renders header and active count", () => {
    const { container } = render(<APIThrottleRuleCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("Throttle Rules");
    expect(container.textContent).toContain("1/2 active");
  });

  it("shows paths and limits", () => {
    const { container } = render(<APIThrottleRuleCard rules={rules} appName="App" />);
    expect(container.textContent).toContain("/api/users/*");
    expect(container.textContent).toContain("100/60s");
  });

  it("shows empty state", () => {
    const { container } = render(<APIThrottleRuleCard rules={[]} appName="App" />);
    expect(container.textContent).toContain("No throttle rules");
  });
});

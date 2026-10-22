import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AlertRulesPanel } from "@/components/alert-rules-panel";

describe("AlertRulesPanel", () => {
  it("renders rules", () => {
    const rules = [{ name: "High CPU", metric: "cpu_usage", operator: "gt", threshold: 80, triggered: true }];
    const { container } = render(<AlertRulesPanel rules={rules} activeCount={1} />);
    expect(container.textContent).toContain("High CPU");
    expect(container.textContent).toContain("1 active");
  });
  it("empty state", () => {
    const { container } = render(<AlertRulesPanel rules={[]} activeCount={0} />);
    expect(container.textContent).toContain("No alert rules");
  });
});

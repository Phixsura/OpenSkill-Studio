import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AutomationRulesList } from "@/components/automation-rules-list";

describe("AutomationRulesList", () => {
  it("shows rules", () => {
    const rules = [{ name: "Auto Grade", triggerEvent: "submission.completed", actionType: "webhook", enabled: true }];
    const { container } = render(<AutomationRulesList rules={rules} canAdd={true} onAdd={vi.fn()} />);
    expect(container.textContent).toContain("Auto Grade");
  });
  it("empty state", () => {
    const { container } = render(<AutomationRulesList rules={[]} canAdd={false} />);
    expect(container.textContent).toContain("No automation");
  });
});

import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AutomationRuleBuilder } from "@/components/automation-rule-builder";

const mockRules = [
  { id: "r1", name: "Deploy Notify", eventType: "deploy", logic: "and" as const,
    conditions: [{ field: "status", operator: "equals", value: "success" }],
    actions: [{ actionType: "send_notification", params: {} }],
    enabled: true, executionCount: 15 },
  { id: "r2", name: "CPU Alert", eventType: "metrics", logic: "and" as const,
    conditions: [{ field: "cpu", operator: "greater_than", value: "90" }],
    actions: [{ actionType: "alert", params: {} }],
    enabled: false, executionCount: 3 },
];

describe("AutomationRuleBuilder", () => {
  it("renders rules with status", () => {
    const { container } = render(<AutomationRuleBuilder rules={mockRules} />);
    expect(container.textContent).toContain("Deploy Notify");
    expect(container.textContent).toContain("1/2 active");
    expect(container.textContent).toContain("×15");
  });

  it("expands to show conditions", () => {
    const { container, getByText } = render(<AutomationRuleBuilder rules={mockRules} />);
    fireEvent.click(getByText("Deploy Notify"));
    expect(container.textContent).toContain("status");
    expect(container.textContent).toContain("equals");
    expect(container.textContent).toContain("send_notification");
  });

  it("calls onToggle", () => {
    const onToggle = vi.fn();
    const { getAllByText } = render(<AutomationRuleBuilder rules={mockRules} onToggle={onToggle} />);
    fireEvent.click(getAllByText("Off")[0]);
    expect(onToggle).toHaveBeenCalledWith("r2");
  });
});

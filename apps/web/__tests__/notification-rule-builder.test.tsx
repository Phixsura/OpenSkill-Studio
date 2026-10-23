import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { NotificationRuleBuilder } from "@/components/notification-rule-builder";

describe("NotificationRuleBuilder", () => {
  const rules = [
    { name: "High Errors", rule_type: "threshold", type_info: { label: "Threshold", icon: "📊" },
      channels: ["email", "slack"], enabled: true },
  ];
  it("renders", () => {
    const { container } = render(
      <NotificationRuleBuilder rules={rules} onToggle={vi.fn()} onDelete={vi.fn()} onCreate={vi.fn()} />
    );
    expect(container.textContent).toContain("Notification Rules");
    expect(container.textContent).toContain("High Errors");
    expect(container.textContent).toContain("📊");
    expect(container.textContent).toContain("email");
    expect(container.textContent).toContain("slack");
  });
  it("delete", () => {
    const fn = vi.fn();
    const { container } = render(
      <NotificationRuleBuilder rules={rules} onToggle={vi.fn()} onDelete={fn} onCreate={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "×")!);
    expect(fn).toHaveBeenCalledWith("High Errors");
  });
});

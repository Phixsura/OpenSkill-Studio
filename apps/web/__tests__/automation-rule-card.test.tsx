import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AutomationRuleCard } from "@/components/automation-rule-card";

const BASE = { name: "Auto Grade", triggerEvent: "submission.completed", actionType: "webhook", enabled: true };

describe("AutomationRuleCard", () => {
  it("renders name", () => {
    const { container } = render(<AutomationRuleCard {...BASE} />);
    expect(container.textContent).toContain("Auto Grade");
  });

  it("shows trigger event", () => {
    const { container } = render(<AutomationRuleCard {...BASE} />);
    expect(container.textContent).toContain("submission.completed");
  });

  it("shows action type", () => {
    const { container } = render(<AutomationRuleCard {...BASE} />);
    expect(container.textContent).toContain("webhook");
  });

  it("shows active status", () => {
    const { container } = render(<AutomationRuleCard {...BASE} onToggle={vi.fn()} />);
    expect(container.textContent).toContain("Active");
  });

  it("shows disabled status", () => {
    const { container } = render(<AutomationRuleCard {...BASE} enabled={false} onToggle={vi.fn()} />);
    expect(container.textContent).toContain("Disabled");
  });

  it("calls onToggle", () => {
    const onToggle = vi.fn();
    const { container } = render(<AutomationRuleCard {...BASE} onToggle={onToggle} />);
    const btn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Active");
    if (btn) fireEvent.click(btn);
    expect(onToggle).toHaveBeenCalledWith(false);
  });

  it("shows rate limit", () => {
    const { container } = render(<AutomationRuleCard {...BASE} executionsPerHour={100} />);
    expect(container.textContent).toContain("100/hour");
  });
});

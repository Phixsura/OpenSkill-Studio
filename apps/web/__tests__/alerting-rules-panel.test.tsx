import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AlertingRulesPanel } from "@/components/alerting-rules-panel";

describe("AlertingRulesPanel", () => {
  const rules = [
    { rule_id: "r1", name: "High Errors", condition: "error_rate > 5", status: "active", notify_channels: ["slack"] },
  ];
  it("renders", () => {
    const { container } = render(
      <AlertingRulesPanel rules={rules} onToggle={vi.fn()} onDelete={vi.fn()} onCreate={vi.fn()} />
    );
    expect(container.textContent).toContain("Alert Rules");
    expect(container.textContent).toContain("High Errors");
    expect(container.textContent).toContain("error_rate > 5");
    expect(container.textContent).toContain("slack");
  });
  it("delete", () => {
    const fn = vi.fn();
    const { container } = render(
      <AlertingRulesPanel rules={rules} onToggle={vi.fn()} onDelete={fn} onCreate={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Delete")!);
    expect(fn).toHaveBeenCalledWith("r1");
  });
});

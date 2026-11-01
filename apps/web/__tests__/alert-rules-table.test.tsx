import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AlertRulesTable } from "@/components/alert-rules-table";

describe("AlertRulesTable", () => {
  it("renders rules with firing", () => {
    const onToggle = vi.fn();
    const { container, getAllByRole } = render(
      <AlertRulesTable onToggle={onToggle}
        rules={[
          { name: "High CPU", metric: "cpu_pct", operator: "gt", threshold: 90, severity: "critical", enabled: true },
          { name: "Low Disk", metric: "disk_free_gb", operator: "lt", threshold: 10, severity: "warning", enabled: true },
        ]}
        triggered={[{ rule: "High CPU", severity: "critical", message: "cpu is 95" }]} />
    );
    expect(container.textContent).toContain("Alert Rules");
    expect(container.textContent).toContain("1 firing");
    expect(container.textContent).toContain("High CPU");
    expect(container.textContent).toContain("Firing");
    expect(container.textContent).toContain("critical");
    const buttons = getAllByRole("button");
    fireEvent.click(buttons[0]);
    expect(onToggle).toHaveBeenCalledWith("High CPU");
  });
});

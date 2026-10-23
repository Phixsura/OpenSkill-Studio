import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AlertRulesPanel } from "@/components/alert-rules-panel";

describe("AlertRulesPanel", () => {
  const rules = [
    { name: "High CPU", metric: "cpu_pct", operator: ">", threshold: 80, status: "firing", channel: "slack", severity: "critical" },
    { name: "Low Disk", metric: "disk_pct", operator: "<", threshold: 10, status: "ok", channel: "email", severity: "warning" },
  ];
  it("renders alert rules", () => {
    const { container } = render(<AlertRulesPanel rules={rules} firing={1} healthy={false} />);
    expect(container.textContent).toContain("High CPU");
    expect(container.textContent).toContain("cpu_pct > 80");
    expect(container.textContent).toContain("firing");
    expect(container.textContent).toContain("1 firing");
  });
});

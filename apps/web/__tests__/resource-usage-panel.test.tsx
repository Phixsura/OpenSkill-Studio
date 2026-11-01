import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ResourceUsagePanel } from "@/components/resource-usage-panel";

describe("ResourceUsagePanel", () => {
  const resources = [
    { name: "CPU", icon: "⚡", value: 45, display: "45%", status: "ok" },
    { name: "Memory", icon: "🧠", value: 93, display: "480/512MB", status: "critical" },
  ];
  it("renders usage", () => {
    const { container } = render(<ResourceUsagePanel resources={resources} overall="critical" />);
    expect(container.textContent).toContain("Resource Usage");
    expect(container.textContent).toContain("CPU");
    expect(container.textContent).toContain("45%");
    expect(container.textContent).toContain("Memory");
    expect(container.textContent).toContain("Alert");
  });
});

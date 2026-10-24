import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HealthStatusIndicator } from "@/components/health-status-indicator";

describe("HealthStatusIndicator", () => {
  it("healthy", () => {
    const { container } = render(<HealthStatusIndicator status="healthy" label="All Systems Go" />);
    expect(container.textContent).toContain("All Systems Go");
    expect(container.querySelector("[class*='bg-green']")).toBeTruthy();
  });
  it("critical", () => {
    const { container } = render(<HealthStatusIndicator status="critical" label="Outage" />);
    expect(container.textContent).toContain("Outage");
    expect(container.querySelector("[class*='bg-red']")).toBeTruthy();
  });
  it("no label", () => {
    const { container } = render(<HealthStatusIndicator status="warning" />);
    expect(container.querySelectorAll("span").length).toBe(1);
  });
});

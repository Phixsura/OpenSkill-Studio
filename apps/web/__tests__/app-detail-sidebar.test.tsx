import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AppDetailSidebar } from "@/components/app-detail-sidebar";

describe("AppDetailSidebar", () => {
  it("shows health score", () => {
    const { container } = render(<AppDetailSidebar healthScore={95} healthStatus="healthy" installCount={42} permissionCount={5} hasSandbox={true} hasUi={false} errorRate={2.5} />);
    expect(container.textContent).toContain("95");
    expect(container.textContent).toContain("healthy");
  });
  it("shows install count", () => {
    const { container } = render(<AppDetailSidebar healthScore={100} healthStatus="healthy" installCount={100} permissionCount={3} hasSandbox={false} hasUi={true} errorRate={0} />);
    expect(container.textContent).toContain("100");
  });
  it("shows sandbox/ui status", () => {
    const { container } = render(<AppDetailSidebar healthScore={90} healthStatus="degraded" installCount={0} permissionCount={0} hasSandbox={true} hasUi={true} errorRate={5} />);
    const checks = (container.textContent?.match(/✅/g) || []).length;
    expect(checks).toBe(2);
  });
});

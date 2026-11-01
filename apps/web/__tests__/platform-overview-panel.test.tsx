import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformOverviewPanel } from "@/components/platform-overview-panel";
describe("PlatformOverviewPanel", () => {
  it("renders", () => {
    const { container } = render(
      <PlatformOverviewPanel overall="operational" healthPct={100}
        totalServices={1590} totalComponents={1590}
        modules={[
          { name: "Extension SDK", status: "operational", services: 159 },
          { name: "Marketplace", status: "operational", services: 159 },
        ]} />
    );
    expect(container.textContent).toContain("OpenSkill Platform: OPERATIONAL");
    expect(container.textContent).toContain("100% healthy");
    expect(container.textContent).toContain("1590 services");
    expect(container.textContent).toContain("Extension SDK");
    expect(container.textContent).toContain("Marketplace");
  });
});

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployFreezePanel } from "@/components/deploy-freeze-panel";
describe("DeployFreezePanel", () => {
  it("renders frozen", () => {
    const { container } = render(
      <DeployFreezePanel frozen={true} reason="Black Friday" remainingHours={24} freezeHistory={3} />
    );
    expect(container.textContent).toContain("DEPLOY FREEZE ACTIVE");
    expect(container.textContent).toContain("Black Friday");
    expect(container.textContent).toContain("24h remaining");
  });
  it("renders unfrozen", () => {
    const { container } = render(
      <DeployFreezePanel frozen={false} reason="" remainingHours={0} freezeHistory={2} />
    );
    expect(container.textContent).toContain("Deployments Allowed");
  });
});

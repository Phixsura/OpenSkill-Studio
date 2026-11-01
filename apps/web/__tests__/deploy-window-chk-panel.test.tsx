import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployWindowChkPanel } from "@/components/deploy-window-chk-panel";
describe("DeployWindowChkPanel", () => {
  it("renders allowed", () => {
    const { container } = render(
      <DeployWindowChkPanel allowed={true} reason="" windowName="business_hours" remainingHours={3} />
    );
    expect(container.textContent).toContain("Deploy Allowed");
    expect(container.textContent).toContain("business_hours");
    expect(container.textContent).toContain("3h remaining");
  });
  it("renders blocked", () => {
    const { container } = render(
      <DeployWindowChkPanel allowed={false} reason="deploy_freeze_active" windowName="" remainingHours={0} />
    );
    expect(container.textContent).toContain("Deploy Blocked");
    expect(container.textContent).toContain("deploy freeze active");
  });
});

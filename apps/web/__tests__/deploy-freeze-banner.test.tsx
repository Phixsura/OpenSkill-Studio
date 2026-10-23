import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DeployFreezeBanner } from "@/components/deploy-freeze-banner";

describe("DeployFreezeBanner", () => {
  it("renders frozen state", () => {
    const { container } = render(
      <DeployFreezeBanner frozen={true} reason="Holiday freeze" freezeCount={1} onCancel={vi.fn()} />
    );
    expect(container.textContent).toContain("Deploy Freeze Active");
    expect(container.textContent).toContain("Holiday freeze");
    expect(container.textContent).toContain("Cancel Freeze");
  });

  it("renders active state", () => {
    const { container } = render(
      <DeployFreezeBanner frozen={false} reason={null} freezeCount={0} onCancel={vi.fn()} />
    );
    expect(container.textContent).toContain("Deployments Active");
  });
});

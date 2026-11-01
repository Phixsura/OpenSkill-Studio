import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CanaryDeployCard } from "@/components/canary-deploy-card";

describe("CanaryDeployCard", () => {
  it("renders promote", () => {
    const { container } = render(
      <CanaryDeployCard verdict="promote" errorDelta={0.02} latencyDeltaPct={5}
        errOk={true} latOk={true} baselineTraffic={10000} canaryTraffic={1000} />
    );
    expect(container.textContent).toContain("Canary Analysis");
    expect(container.textContent).toContain("promote");
    expect(container.textContent).toContain("10,000");
    expect(container.textContent).toContain("1,000");
  });
});

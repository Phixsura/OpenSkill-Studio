import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeployCadencePanel } from "@/components/deploy-cadence-panel";
describe("DeployCadencePanel", () => {
  it("renders", () => {
    const { container } = render(
      <DeployCadencePanel totalDeploys={60} deploysPerDay={2} level="elite"
        label="On-demand" peakDay="2026-10-15" peakCount={5} servicesDeployed={8} />
    );
    expect(container.textContent).toContain("Deploy Cadence");
    expect(container.textContent).toContain("On-demand");
    expect(container.textContent).toContain("2/day");
    expect(container.textContent).toContain("60");
    expect(container.textContent).toContain("2026-10-15");
    expect(container.textContent).toContain("8");
  });
});

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetBuildkitePanel } from "@/components/fleet-buildkite-panel";
describe("FleetBuildkitePanel", () => { it("renders", () => {
    const { container } = render(<FleetBuildkitePanel pipelines={20} passing={19} agents={50} avgQueue={10} />);
    expect(container.textContent).toContain("Buildkite");
    expect(container.textContent).toContain("50 agents");
}); });

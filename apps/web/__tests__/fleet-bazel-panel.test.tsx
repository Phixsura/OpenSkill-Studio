import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetBazelPanel } from "@/components/fleet-bazel-panel";
describe("FleetBazelPanel", () => { it("renders", () => {
    const { container } = render(<FleetBazelPanel totalBuilds={100} avgCacheHit={85} avgBuild={60} remoteExec={50} fast={true} />);
    expect(container.textContent).toContain("Bazel");
    expect(container.textContent).toContain("Fast builds");
}); });

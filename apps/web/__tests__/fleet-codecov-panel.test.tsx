import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCodecovPanel } from "@/components/fleet-codecov-panel";
describe("FleetCodecovPanel", () => { it("renders", () => {
    const { container } = render(<FleetCodecovPanel total={30} withCodecov={25} avgCoverage={75} declining={3} />);
    expect(container.textContent).toContain("Codecov");
    expect(container.textContent).toContain("3 declining");
}); });

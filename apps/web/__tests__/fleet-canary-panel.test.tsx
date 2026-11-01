import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCanaryPanel } from "@/components/fleet-canary-panel";
describe("FleetCanaryPanel", () => { it("renders", () => {
    const { container } = render(<FleetCanaryPanel activeCanaries={1} promoted={2} failed={0} total={3} />);
    expect(container.textContent).toContain("Canary Deploys");
    expect(container.textContent).toContain("1 active");
}); });

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSpacePanel } from "@/components/fleet-space-panel";
describe("FleetSpacePanel", () => { it("renders", () => {
    const { container } = render(<FleetSpacePanel score={75} weakDimensions={["communication"]} balanced={false} />);
    expect(container.textContent).toContain("SPACE Framework");
    expect(container.textContent).toContain("communication");
}); });

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCometPanel } from "@/components/fleet-comet-panel";
describe("FleetCometPanel", () => { it("renders", () => {
    const { container } = render(<FleetCometPanel workspaces={5} active={5} experiments={20000} panels={500} />);
    expect(container.textContent).toContain("Comet");
}); });

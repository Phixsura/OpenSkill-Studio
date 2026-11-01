import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetHexPanel } from "@/components/fleet-hex-panel";
describe("FleetHexPanel", () => { it("renders", () => {
    const { container } = render(<FleetHexPanel workspaces={5} active={5} projects={200} runs={10000} />);
    expect(container.textContent).toContain("Hex");
}); });

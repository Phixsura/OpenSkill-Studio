import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetVectorizePanel } from "@/components/fleet-vectorize-panel";
describe("FleetVectorizePanel", () => { it("renders", () => {
    const { container } = render(<FleetVectorizePanel indexes={5} active={5} vectors={25000000} queries={5000000} />);
    expect(container.textContent).toContain("Vectorize");
}); });

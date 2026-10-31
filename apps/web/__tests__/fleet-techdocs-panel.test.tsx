import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTechdocsPanel } from "@/components/fleet-techdocs-panel";
describe("FleetTechdocsPanel", () => { it("renders", () => {
    const { container } = render(<FleetTechdocsPanel total={50} withTechdocs={40} buildsOk={38} coveragePct={80} />);
    expect(container.textContent).toContain("TechDocs");
    expect(container.textContent).toContain("80%");
}); });

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAngularPanel } from "@/components/fleet-angular-panel";
describe("FleetAngularPanel", () => { it("renders", () => {
    const { container } = render(<FleetAngularPanel apps={10} deployed={10} components={500} modules={50} avgBundle={400} />);
    expect(container.textContent).toContain("Angular");
    expect(container.textContent).toContain("500 components");
}); });

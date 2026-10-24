import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetFeatAdoptPanel } from "@/components/fleet-feat-adopt-panel";
describe("FleetFeatAdoptPanel", () => { it("renders", () => {
    const { container } = render(<FleetFeatAdoptPanel total={20} widelyAdopted={15} avgAdoption={72} good={true} />);
    expect(container.textContent).toContain("Feature Adoption");
    expect(container.textContent).toContain("72%");
}); });

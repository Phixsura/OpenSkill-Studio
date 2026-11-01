import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetFeatureAdoptionV9Panel } from "@/components/fleet-feature-adoption-v9-panel";
describe("FleetFeatureAdoptionV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetFeatureAdoptionV9Panel features={50} adoption={85} />);
    expect(container.textContent).toContain("Feature Adoption v9");
}); });

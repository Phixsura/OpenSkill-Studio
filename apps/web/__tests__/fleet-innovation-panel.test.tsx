import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetInnovationPanel } from "@/components/fleet-innovation-panel";
describe("FleetInnovationPanel", () => { it("renders", () => {
    const { container } = render(<FleetInnovationPanel newFeatures={20} experiments={10} adoptionRate={80} index={32.5} innovative={false} />);
    expect(container.textContent).toContain("Innovation Index");
    expect(container.textContent).toContain("32.5");
}); });

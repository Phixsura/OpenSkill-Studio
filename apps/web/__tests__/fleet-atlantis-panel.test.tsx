import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAtlantisPanel } from "@/components/fleet-atlantis-panel";
describe("FleetAtlantisPanel", () => { it("renders", () => {
    const { container } = render(<FleetAtlantisPanel total={20} enabled={18} plans={50} applies={30} />);
    expect(container.textContent).toContain("Atlantis");
    expect(container.textContent).toContain("50 plans");
}); });

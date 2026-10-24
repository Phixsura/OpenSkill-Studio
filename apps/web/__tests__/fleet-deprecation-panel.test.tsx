import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDeprecationPanel } from "@/components/fleet-deprecation-panel";
describe("FleetDeprecationPanel", () => { it("renders", () => {
    const { container } = render(<FleetDeprecationPanel total={30} deprecated={5} stillUsed={3} safeToRemove={2} />);
    expect(container.textContent).toContain("API Deprecation");
    expect(container.textContent).toContain("2 removable");
}); });

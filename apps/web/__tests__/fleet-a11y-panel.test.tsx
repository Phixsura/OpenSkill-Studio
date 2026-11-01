import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetA11yPanel } from "@/components/fleet-a11y-panel";
describe("FleetA11yPanel", () => { it("renders", () => {
    const { container } = render(<FleetA11yPanel total={30} wcagAa={28} wcagAaa={10} score={93.3} compliant={false} />);
    expect(container.textContent).toContain("Accessibility");
    expect(container.textContent).toContain("93.3%");
}); });

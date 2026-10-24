import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRlConfigPanel } from "@/components/fleet-rl-config-panel";
describe("FleetRlConfigPanel", () => { it("renders", () => {
    const { container } = render(<FleetRlConfigPanel total={20} protected={18} unprotected={2} fullyCovered={false} />);
    expect(container.textContent).toContain("Rate Limits");
    expect(container.textContent).toContain("2 endpoints unprotected");
}); });

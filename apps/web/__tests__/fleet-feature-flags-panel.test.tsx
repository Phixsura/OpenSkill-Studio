import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetFeatureFlagsPanel } from "@/components/fleet-feature-flags-panel";
describe("FleetFeatureFlagsPanel", () => { it("renders", () => {
    const { container } = render(<FleetFeatureFlagsPanel total={10} enabled={7} stale={2} needsCleanup={true} />);
    expect(container.textContent).toContain("Feature Flags");
    expect(container.textContent).toContain("2 stale");
}); });

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetFeatureFlagV9Panel } from "@/components/fleet-feature-flag-v9-panel";
describe("FleetFeatureFlagV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetFeatureFlagV9Panel total={200} enabled={180} />);
    expect(container.textContent).toContain("Feature Flags v9");
}); });

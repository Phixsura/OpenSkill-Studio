import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAmplifyPanel } from "@/components/fleet-amplify-panel";
describe("FleetAmplifyPanel", () => { it("renders", () => {
    const { container } = render(<FleetAmplifyPanel apps={10} deployed={10} backends={20} branches={30} />);
    expect(container.textContent).toContain("Amplify");
}); });

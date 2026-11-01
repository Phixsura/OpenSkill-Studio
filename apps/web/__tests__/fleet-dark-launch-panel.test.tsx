import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDarkLaunchPanel } from "@/components/fleet-dark-launch-panel";
describe("FleetDarkLaunchPanel", () => { it("renders", () => {
    const { container } = render(<FleetDarkLaunchPanel total={10} darkLaunching={2} avgShadowPct={15} />);
    expect(container.textContent).toContain("Dark Launch");
    expect(container.textContent).toContain("15% shadow");
}); });

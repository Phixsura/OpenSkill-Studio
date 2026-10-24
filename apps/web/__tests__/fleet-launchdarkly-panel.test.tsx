import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetLaunchdarklyPanel } from "@/components/fleet-launchdarkly-panel";
describe("FleetLaunchdarklyPanel", () => { it("renders", () => {
    const { container } = render(<FleetLaunchdarklyPanel total={100} active={90} stale={15} targeting={50} />);
    expect(container.textContent).toContain("LaunchDarkly");
    expect(container.textContent).toContain("15 stale");
}); });

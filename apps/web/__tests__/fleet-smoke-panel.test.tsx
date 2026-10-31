import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSmokePanel } from "@/components/fleet-smoke-panel";
describe("FleetSmokePanel", () => { it("renders", () => {
    const { container } = render(<FleetSmokePanel total={10} passed={9} failed={1} allPassed={false} />);
    expect(container.textContent).toContain("Smoke Tests");
    expect(container.textContent).toContain("1/10 failed");
}); });

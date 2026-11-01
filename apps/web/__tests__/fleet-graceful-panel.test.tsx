import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGracefulPanel } from "@/components/fleet-graceful-panel";
describe("FleetGracefulPanel", () => { it("renders", () => {
    const { container } = render(<FleetGracefulPanel total={20} graceful={18} forcedKill={2} compliant={false} />);
    expect(container.textContent).toContain("Graceful Shutdown");
    expect(container.textContent).toContain("2 forced kills");
}); });

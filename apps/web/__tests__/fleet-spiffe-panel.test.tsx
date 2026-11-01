import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSpiffePanel } from "@/components/fleet-spiffe-panel";
describe("FleetSpiffePanel", () => { it("renders", () => {
    const { container } = render(<FleetSpiffePanel total={30} withSvid={28} expired={1} coveragePct={93.3} />);
    expect(container.textContent).toContain("SPIFFE");
    expect(container.textContent).toContain("1 expired");
}); });

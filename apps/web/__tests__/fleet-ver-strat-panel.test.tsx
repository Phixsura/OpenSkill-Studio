import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetVerStratPanel } from "@/components/fleet-ver-strat-panel";
describe("FleetVerStratPanel", () => { it("renders", () => {
    const { container } = render(<FleetVerStratPanel total={10} consistent={false} />);
    expect(container.textContent).toContain("Versioning Strategy");
    expect(container.textContent).toContain("Mixed strategies");
}); });

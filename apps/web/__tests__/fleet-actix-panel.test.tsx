import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetActixPanel } from "@/components/fleet-actix-panel";
describe("FleetActixPanel", () => { it("renders", () => {
    const { container } = render(<FleetActixPanel services={3} running={3} rps={900000} p99={1.5} />);
    expect(container.textContent).toContain("Actix");
    expect(container.textContent).toContain("900,000");
}); });

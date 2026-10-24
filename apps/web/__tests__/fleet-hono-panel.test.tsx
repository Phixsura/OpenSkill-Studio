import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetHonoPanel } from "@/components/fleet-hono-panel";
describe("FleetHonoPanel", () => { it("renders", () => {
    const { container } = render(<FleetHonoPanel apps={10} deployed={10} rps={500000} avgLatency={3} />);
    expect(container.textContent).toContain("Hono");
    expect(container.textContent).toContain("500,000");
}); });

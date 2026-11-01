import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGarnetPanel } from "@/components/fleet-garnet-panel";
describe("FleetGarnetPanel", () => { it("renders", () => {
    const { container } = render(<FleetGarnetPanel instances={3} healthy={3} opsPerSec={5000000} p99Us={30} />);
    expect(container.textContent).toContain("Garnet");
    expect(container.textContent).toContain("5,000,000");
}); });

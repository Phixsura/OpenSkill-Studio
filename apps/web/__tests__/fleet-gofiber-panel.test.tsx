import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGofiberPanel } from "@/components/fleet-gofiber-panel";
describe("FleetGofiberPanel", () => { it("renders", () => {
    const { container } = render(<FleetGofiberPanel services={5} running={5} rps={500000} goroutines={25000} />);
    expect(container.textContent).toContain("Go Fiber");
    expect(container.textContent).toContain("500,000");
}); });

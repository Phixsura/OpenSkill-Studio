import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDenoPanel } from "@/components/fleet-deno-panel";
describe("FleetDenoPanel", () => { it("renders", () => {
    const { container } = render(<FleetDenoPanel projects={10} deployed={10} requests={10000000} avgIsolate={8} />);
    expect(container.textContent).toContain("Deno Deploy");
    expect(container.textContent).toContain("10,000,000");
}); });

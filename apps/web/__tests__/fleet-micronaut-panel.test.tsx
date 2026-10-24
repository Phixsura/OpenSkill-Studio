import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMicronautPanel } from "@/components/fleet-micronaut-panel";
describe("FleetMicronautPanel", () => { it("renders", () => {
    const { container } = render(<FleetMicronautPanel services={8} running={8} graalvm={6} avgMemory={100} />);
    expect(container.textContent).toContain("Micronaut");
    expect(container.textContent).toContain("6 GraalVM");
}); });

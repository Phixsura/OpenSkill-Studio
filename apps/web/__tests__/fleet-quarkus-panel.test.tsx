import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetQuarkusPanel } from "@/components/fleet-quarkus-panel";
describe("FleetQuarkusPanel", () => { it("renders", () => {
    const { container } = render(<FleetQuarkusPanel services={10} running={10} native={8} avgStartup={45} />);
    expect(container.textContent).toContain("Quarkus");
    expect(container.textContent).toContain("8 native");
}); });

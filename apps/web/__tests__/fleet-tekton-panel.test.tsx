import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTektonPanel } from "@/components/fleet-tekton-panel";
describe("FleetTektonPanel", () => { it("renders", () => {
    const { container } = render(<FleetTektonPanel total={50} succeeded={45} failed={3} running={2} avgDuration={8} />);
    expect(container.textContent).toContain("Tekton");
    expect(container.textContent).toContain("avg 8min");
}); });

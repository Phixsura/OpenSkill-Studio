import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetKedaPanel } from "@/components/fleet-keda-panel";
describe("FleetKedaPanel", () => { it("renders", () => {
    const { container } = render(<FleetKedaPanel total={10} active={8} triggered={3} idle={2} />);
    expect(container.textContent).toContain("KEDA");
    expect(container.textContent).toContain("3 triggered");
}); });

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetNovuPanel } from "@/components/fleet-novu-panel";
describe("FleetNovuPanel", () => { it("renders", () => {
    const { container } = render(<FleetNovuPanel environments={3} active={3} notifications={5000000} channels={8} />);
    expect(container.textContent).toContain("Novu");
}); });

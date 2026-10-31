import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetK9sPanel } from "@/components/fleet-k9s-panel";
describe("FleetK9sPanel", () => { it("renders", () => {
    const { container } = render(<FleetK9sPanel totalUsers={50} active={30} commands={15000} />);
    expect(container.textContent).toContain("K9s");
    expect(container.textContent).toContain("15,000 commands");
}); });

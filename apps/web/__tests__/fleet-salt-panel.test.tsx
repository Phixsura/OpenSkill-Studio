import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSaltPanel } from "@/components/fleet-salt-panel";
describe("FleetSaltPanel", () => { it("renders", () => {
    const { container } = render(<FleetSaltPanel total={50} connected={48} disconnected={2} />);
    expect(container.textContent).toContain("SaltStack");
    expect(container.textContent).toContain("2 disconnected");
}); });

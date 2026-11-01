import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGwAuthPanel } from "@/components/fleet-gw-auth-panel";
describe("FleetGwAuthPanel", () => { it("renders", () => {
    const { container } = render(<FleetGwAuthPanel total={50} noAuth={3} secure={false} />);
    expect(container.textContent).toContain("Gateway Auth");
    expect(container.textContent).toContain("3 endpoints without");
}); });

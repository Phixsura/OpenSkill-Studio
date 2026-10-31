import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTimeoutBgtPanel } from "@/components/fleet-timeout-bgt-panel";
describe("FleetTimeoutBgtPanel", () => { it("renders", () => {
    const { container } = render(<FleetTimeoutBgtPanel chains={10} overBudget={2} avgUtil={60} healthy={false} />);
    expect(container.textContent).toContain("Timeout Budget");
    expect(container.textContent).toContain("2 over budget");
}); });

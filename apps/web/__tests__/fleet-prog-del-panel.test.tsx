import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetProgDelPanel } from "@/components/fleet-prog-del-panel";
describe("FleetProgDelPanel", () => { it("renders", () => {
    const { container } = render(<FleetProgDelPanel total={5} inProgress={2} completed={2} paused={1} />);
    expect(container.textContent).toContain("Progressive Delivery");
}); });

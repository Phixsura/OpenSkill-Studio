import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCbStatusPanel } from "@/components/fleet-cb-status-panel";
describe("FleetCbStatusPanel", () => { it("renders", () => {
    const { container } = render(<FleetCbStatusPanel total={5} open={1} halfOpen={1} closed={3} healthy={false} />);
    expect(container.textContent).toContain("Circuit Breakers");
    expect(container.textContent).toContain("1 circuits open");
}); });

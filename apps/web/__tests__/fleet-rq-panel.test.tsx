import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRqPanel } from "@/components/fleet-rq-panel";
describe("FleetRqPanel", () => { it("renders", () => {
    const { container } = render(<FleetRqPanel total={5} overThreshold={1} healthy={false} />);
    expect(container.textContent).toContain("Resource Quotas");
    expect(container.textContent).toContain("1/5 over");
}); });

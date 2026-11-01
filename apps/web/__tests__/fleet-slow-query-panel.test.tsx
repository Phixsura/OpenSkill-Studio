import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSlowQueryPanel } from "@/components/fleet-slow-query-panel";
describe("FleetSlowQueryPanel", () => { it("renders", () => {
    const { container } = render(<FleetSlowQueryPanel total={100} slow={10} verySlow={2} needsAttention={true} />);
    expect(container.textContent).toContain("Slow Queries");
    expect(container.textContent).toContain("Query optimization needed");
}); });

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetTurborepoPanel } from "@/components/fleet-turborepo-panel";
describe("FleetTurborepoPanel", () => { it("renders", () => {
    const { container } = render(<FleetTurborepoPanel totalTasks={100} cacheHits={80} cacheMisses={20} timeSaved={2400} hitRate={80} />);
    expect(container.textContent).toContain("Turborepo");
    expect(container.textContent).toContain("80% cache hit");
}); });

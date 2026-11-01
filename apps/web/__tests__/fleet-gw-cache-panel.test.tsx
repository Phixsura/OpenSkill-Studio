import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGwCachePanel } from "@/components/fleet-gw-cache-panel";
describe("FleetGwCachePanel", () => { it("renders", () => {
    const { container } = render(<FleetGwCachePanel total={20} cached={15} hitRate={90} effective={true} />);
    expect(container.textContent).toContain("Gateway Cache");
    expect(container.textContent).toContain("Effective caching");
}); });

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDaggerPanel } from "@/components/fleet-dagger-panel";
describe("FleetDaggerPanel", () => { it("renders", () => {
    const { container } = render(<FleetDaggerPanel pipelines={10} cacheHits={200} operations={1000} avgDuration={120} />);
    expect(container.textContent).toContain("Dagger");
    expect(container.textContent).toContain("200 cache hits");
}); });

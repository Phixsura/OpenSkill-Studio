import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCacheEvictPanel } from "@/components/fleet-cache-evict-panel";
describe("FleetCacheEvictPanel", () => { it("renders", () => {
    const { container } = render(<FleetCacheEvictPanel totalEvictions={250} highEviction={1} needsResize={true} />);
    expect(container.textContent).toContain("Cache Evictions");
    expect(container.textContent).toContain("need resizing");
}); });

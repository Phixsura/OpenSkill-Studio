import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCacheInvalidationV9Panel } from "@/components/fleet-cache-invalidation-v9-panel";
describe("FleetCacheInvalidationV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCacheInvalidationV9Panel caches={10} invalidations={500} />);
    expect(container.textContent).toContain("Cache Invalidation v9");
}); });

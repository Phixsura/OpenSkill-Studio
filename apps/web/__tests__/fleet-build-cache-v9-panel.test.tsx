import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetBuildCacheV9Panel } from "@/components/fleet-build-cache-v9-panel";
describe("FleetBuildCacheV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetBuildCacheV9Panel caches={5} hitRate={90} />);
    expect(container.textContent).toContain("Build Cache v9");
}); });

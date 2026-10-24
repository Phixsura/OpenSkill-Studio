import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCdnCacheV9Panel } from "@/components/fleet-cdn-cache-v9-panel";
describe("FleetCdnCacheV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCdnCacheV9Panel pops={50} hitRatio={0.95} />);
    expect(container.textContent).toContain("CDN Cache v9");
}); });

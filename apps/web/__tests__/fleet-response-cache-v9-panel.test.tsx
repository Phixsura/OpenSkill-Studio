import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetResponseCacheV9Panel } from "@/components/fleet-response-cache-v9-panel";
describe("FleetResponseCacheV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetResponseCacheV9Panel caches={10} hitRate={90} />);
    expect(container.textContent).toContain("Response Cache v9");
}); });

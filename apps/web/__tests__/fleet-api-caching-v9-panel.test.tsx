import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiCachingV9Panel } from "@/components/fleet-api-caching-v9-panel";
describe("FleetApiCachingV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiCachingV9Panel endpoints={100} hitRate={90} />);
    expect(container.textContent).toContain("API Caching v9");
}); });

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiCachePolicyV9Panel } from "@/components/fleet-api-cache-policy-v9-panel";
describe("FleetApiCachePolicyV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiCachePolicyV9Panel policies={30} ttl={300} />);
    expect(container.textContent).toContain("Cache Policy v9");
}); });

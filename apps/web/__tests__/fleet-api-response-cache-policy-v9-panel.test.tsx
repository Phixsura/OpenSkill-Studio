import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiResponseCachePolicyV9Panel } from "@/components/fleet-api-response-cache-policy-v9-panel";
describe("FleetApiResponseCachePolicyV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiResponseCachePolicyV9Panel policies={30} hitRate={90} />);
    expect(container.textContent).toContain("Response Cache Policy v9");
}); });

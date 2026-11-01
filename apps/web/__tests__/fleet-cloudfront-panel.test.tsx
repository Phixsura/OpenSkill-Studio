import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCloudfrontPanel } from "@/components/fleet-cloudfront-panel";
describe("FleetCloudfrontPanel", () => { it("renders", () => {
    const { container } = render(<FleetCloudfrontPanel distributions={10} deployed={10} requests={500000000} cacheHit={95} />);
    expect(container.textContent).toContain("CloudFront");
    expect(container.textContent).toContain("95% hit");
}); });

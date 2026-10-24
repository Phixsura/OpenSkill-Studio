import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetRateLimiterV9Panel } from "@/components/fleet-rate-limiter-v9-panel";
describe("FleetRateLimiterV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetRateLimiterV9Panel endpoints={50} throttlePct={0.05} />);
    expect(container.textContent).toContain("Rate Limiter v9");
}); });

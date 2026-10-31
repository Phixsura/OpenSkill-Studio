import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiRatelimV2Panel } from "@/components/fleet-ai-ratelim-v2-panel";
describe("FleetAiRatelimV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiRatelimV2Panel limiters={5} active={5} throttled={10000} total={50000000} throttlePct={0.02} />);
    expect(container.textContent).toContain("Rate Limiter");
}); });

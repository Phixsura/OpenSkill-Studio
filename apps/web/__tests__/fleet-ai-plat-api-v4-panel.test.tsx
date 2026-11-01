import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatApiV4Panel } from "@/components/fleet-ai-plat-api-v4-panel";
describe("FleetAiPlatApiV4Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatApiV4Panel gateways={5} active={5} endpoints={2000} requests={50000000000} p99={15} errorRate={0.005} />);
    expect(container.textContent).toContain("AI API v4");
}); });

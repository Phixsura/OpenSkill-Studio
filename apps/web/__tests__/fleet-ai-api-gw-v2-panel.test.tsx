import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiApiGwV2Panel } from "@/components/fleet-ai-api-gw-v2-panel";
describe("FleetAiApiGwV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiApiGwV2Panel gateways={3} active={3} routes={1000} requests={5000000000} authMethods={8} />);
    expect(container.textContent).toContain("API Gateway v2");
}); });

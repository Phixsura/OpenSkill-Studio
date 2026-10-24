import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiApiGwPanel } from "@/components/fleet-ai-api-gw-panel";
describe("FleetAiApiGwPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiApiGwPanel gateways={3} active={3} providers={15} requests={60000000} cost={300000} />);
    expect(container.textContent).toContain("AI API Gateway");
}); });

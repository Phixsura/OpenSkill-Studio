import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiMultiCloudV2Panel } from "@/components/fleet-ai-multi-cloud-v2-panel";
describe("FleetAiMultiCloudV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiMultiCloudV2Panel managers={3} active={3} clouds={["aws", "gcp", "azure"]} deployments={1000} failover={true} />);
    expect(container.textContent).toContain("Multi-Cloud v2");
}); });

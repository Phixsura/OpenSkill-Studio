import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiResQuotaV2Panel } from "@/components/fleet-ai-res-quota-v2-panel";
describe("FleetAiResQuotaV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiResQuotaV2Panel quotas={5} active={5} namespaces={100} gpus={1000} memoryGb={50000} />);
    expect(container.textContent).toContain("Resource Quota v2");
}); });

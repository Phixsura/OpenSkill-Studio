import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelGovV2Panel } from "@/components/fleet-ai-model-gov-v2-panel";
describe("FleetAiModelGovV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelGovV2Panel frameworks={3} active={3} models={1000} policies={500} compliance={99.5} approvals={100} />);
    expect(container.textContent).toContain("Model Governance v2");
}); });

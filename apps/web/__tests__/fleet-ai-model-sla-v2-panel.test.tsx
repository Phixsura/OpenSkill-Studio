import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelSlaV2Panel } from "@/components/fleet-ai-model-sla-v2-panel";
describe("FleetAiModelSlaV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelSlaV2Panel slas={5} active={5} models={500} met={498} breached={2} />);
    expect(container.textContent).toContain("Model SLA v2");
}); });

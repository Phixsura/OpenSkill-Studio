import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelMonPanel } from "@/components/fleet-ai-model-mon-panel";
describe("FleetAiModelMonPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelMonPanel monitors={10} active={10} models={100} driftAlerts={0} perfAlerts={0} stable={true} />);
    expect(container.textContent).toContain("Model Monitoring");
    expect(container.textContent).toContain("Stable");
}); });

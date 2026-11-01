import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiBiasPanel } from "@/components/fleet-ai-bias-panel";
describe("FleetAiBiasPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiBiasPanel monitors={10} active={10} modelsAudited={100} biasAlerts={0} fair={true} />);
    expect(container.textContent).toContain("Bias Detection");
    expect(container.textContent).toContain("Fair");
}); });

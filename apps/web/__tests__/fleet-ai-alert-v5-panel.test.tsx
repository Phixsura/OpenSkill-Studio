import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiAlertV5Panel } from "@/components/fleet-ai-alert-v5-panel";
describe("FleetAiAlertV5Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiAlertV5Panel systems={4} active={4} alerts={1000} acked={990} autoResolved={800} noiseReduction={80} />);
    expect(container.textContent).toContain("Alerting v5");
}); });

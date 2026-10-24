import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTelemetryPanel } from "@/components/fleet-ai-telemetry-panel";
describe("FleetAiTelemetryPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiTelemetryPanel collectors={5} active={5} spans={50000000} tokens={25000000000} cost={250000} />);
    expect(container.textContent).toContain("AI Telemetry");
}); });

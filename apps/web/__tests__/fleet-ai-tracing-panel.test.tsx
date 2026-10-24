import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTracingPanel } from "@/components/fleet-ai-tracing-panel";
describe("FleetAiTracingPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiTracingPanel tracers={4} active={4} traces={200000000} spans={2000000000} avgDepth={10} />);
    expect(container.textContent).toContain("AI Tracing");
}); });

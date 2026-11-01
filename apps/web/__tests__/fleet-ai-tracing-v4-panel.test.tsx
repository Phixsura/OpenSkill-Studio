import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTracingV4Panel } from "@/components/fleet-ai-tracing-v4-panel";
describe("FleetAiTracingV4Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiTracingV4Panel systems={5} active={5} traces={5000000000} spans={50000000000} sampling={15} />);
    expect(container.textContent).toContain("AI Tracing v4");
}); });

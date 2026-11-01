import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPipeV3Panel } from "@/components/fleet-ai-pipe-v3-panel";
describe("FleetAiPipeV3Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPipeV3Panel pipelines={5} active={5} stages={100} executions={500000} successRate={99.5} />);
    expect(container.textContent).toContain("Pipeline v3");
}); });

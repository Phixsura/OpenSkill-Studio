import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiStreamPanel } from "@/components/fleet-ai-stream-panel";
describe("FleetAiStreamPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiStreamPanel endpoints={10} active={10} activeStreams={5000} tokensStreamed={2000000000} />);
    expect(container.textContent).toContain("AI Streaming");
}); });

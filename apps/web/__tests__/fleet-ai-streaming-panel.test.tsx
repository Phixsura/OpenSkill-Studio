import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiStreamingPanel } from "@/components/fleet-ai-streaming-panel";
describe("FleetAiStreamingPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiStreamingPanel streams={10} active={10} connections={200000} tps={500000} ttft={80} />);
    expect(container.textContent).toContain("AI Streaming");
}); });

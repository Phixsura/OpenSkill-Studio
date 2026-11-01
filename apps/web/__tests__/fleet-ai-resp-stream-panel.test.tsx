import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiRespStreamPanel } from "@/components/fleet-ai-resp-stream-panel";
describe("FleetAiRespStreamPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiRespStreamPanel streamers={5} active={5} streams={50000000} tokens={500000000000} ttft={50} />);
    expect(container.textContent).toContain("Response Streamer");
}); });

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiRespCompPanel } from "@/components/fleet-ai-resp-comp-panel";
describe("FleetAiRespCompPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiRespCompPanel compressors={3} active={3} responses={200000000} ratio={4} savedGb={2000} />);
    expect(container.textContent).toContain("Response Compressor");
}); });

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiAudiogenPanel } from "@/components/fleet-ai-audiogen-panel";
describe("FleetAiAudiogenPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiAudiogenPanel services={3} active={3} clips={300000} hours={15000} />);
    expect(container.textContent).toContain("AI Audio Gen");
}); });

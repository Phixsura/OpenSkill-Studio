import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiVoiceClnPanel } from "@/components/fleet-ai-voice-cln-panel";
describe("FleetAiVoiceClnPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiVoiceClnPanel systems={3} active={3} voices={50000} generations={2000000} mos={4.7} />);
    expect(container.textContent).toContain("Voice Clone");
}); });

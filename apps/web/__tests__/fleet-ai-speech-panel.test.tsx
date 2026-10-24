import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSpeechPanel } from "@/components/fleet-ai-speech-panel";
describe("FleetAiSpeechPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSpeechPanel services={5} active={5} sttHours={50000} ttsChars={2000000000} />);
    expect(container.textContent).toContain("AI Speech");
}); });

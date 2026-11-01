import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSpeechPanel } from "@/components/fleet-ai-speech-panel";
describe("FleetAiSpeechPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSpeechPanel services={6} active={6} hours={50000} languages={30} wer={2.5} />);
    expect(container.textContent).toContain("AI Speech");
}); });

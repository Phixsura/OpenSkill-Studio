import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTokenizerPanel } from "@/components/fleet-ai-tokenizer-panel";
describe("FleetAiTokenizerPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiTokenizerPanel tokenizers={4} active={4} vocabSize={200000} tokens={100000000000} compression={4.2} />);
    expect(container.textContent).toContain("AI Tokenizer");
}); });

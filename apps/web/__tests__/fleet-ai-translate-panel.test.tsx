import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTranslatePanel } from "@/components/fleet-ai-translate-panel";
describe("FleetAiTranslatePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiTranslatePanel translators={5} active={5} translations={10000000} langPairs={200} bleu={60} />);
    expect(container.textContent).toContain("AI Translation");
}); });

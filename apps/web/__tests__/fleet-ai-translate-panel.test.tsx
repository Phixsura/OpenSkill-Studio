import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTranslatePanel } from "@/components/fleet-ai-translate-panel";
describe("FleetAiTranslatePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiTranslatePanel services={5} active={5} translations={10000000} languages={120} />);
    expect(container.textContent).toContain("AI Translation");
}); });

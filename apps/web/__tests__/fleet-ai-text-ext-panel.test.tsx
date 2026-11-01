import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTextExtPanel } from "@/components/fleet-ai-text-ext-panel";
describe("FleetAiTextExtPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiTextExtPanel extractors={4} active={4} extracted={20000000} types={6} accuracy={99} />);
    expect(container.textContent).toContain("Text Extractor");
}); });

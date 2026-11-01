import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiNerPanel } from "@/components/fleet-ai-ner-panel";
describe("FleetAiNerPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiNerPanel extractors={4} active={4} docs={5000000} entities={200000000} types={30} f1={0.96} />);
    expect(container.textContent).toContain("AI NER");
}); });

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiNerPanel } from "@/components/fleet-ai-ner-panel";
describe("FleetAiNerPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiNerPanel services={5} active={5} docs={5000000} entities={100000000} />);
    expect(container.textContent).toContain("AI NER");
}); });

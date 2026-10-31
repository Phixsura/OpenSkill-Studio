import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTextClsPanel } from "@/components/fleet-ai-text-cls-panel";
describe("FleetAiTextClsPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiTextClsPanel classifiers={4} active={4} classified={20000000} labels={200} zeroShot={70} f1={0.95} />);
    expect(container.textContent).toContain("Text Classifier");
}); });

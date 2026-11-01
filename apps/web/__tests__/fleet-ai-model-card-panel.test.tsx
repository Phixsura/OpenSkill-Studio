import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelCardPanel } from "@/components/fleet-ai-model-card-panel";
describe("FleetAiModelCardPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelCardPanel cards={5} active={5} models={500} completeness={97} sections={15} />);
    expect(container.textContent).toContain("Model Card");
}); });

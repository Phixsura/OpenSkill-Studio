import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiIntentClsPanel } from "@/components/fleet-ai-intent-cls-panel";
describe("FleetAiIntentClsPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiIntentClsPanel classifiers={4} active={4} classified={50000000} intents={500} accuracy={97} />);
    expect(container.textContent).toContain("Intent Classifier");
}); });

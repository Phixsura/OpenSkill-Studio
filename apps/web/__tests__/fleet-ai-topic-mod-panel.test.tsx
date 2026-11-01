import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTopicModPanel } from "@/components/fleet-ai-topic-mod-panel";
describe("FleetAiTopicModPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiTopicModPanel modelers={3} active={3} docs={50000000} topics={1000} coherence={0.82} />);
    expect(container.textContent).toContain("Topic Modeler");
}); });

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiConvMemPanel } from "@/components/fleet-ai-conv-mem-panel";
describe("FleetAiConvMemPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiConvMemPanel stores={3} active={3} conversations={2000000} messages={200000000} avgContext={64000} />);
    expect(container.textContent).toContain("Conversation Memory");
}); });

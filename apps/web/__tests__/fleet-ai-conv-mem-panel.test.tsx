import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiConvMemPanel } from "@/components/fleet-ai-conv-mem-panel";
describe("FleetAiConvMemPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiConvMemPanel stores={5} active={5} conversations={50000000} messages={500000000} />);
    expect(container.textContent).toContain("Conv Memory");
}); });

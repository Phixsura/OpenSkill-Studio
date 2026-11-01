import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiTextgenPanel } from "@/components/fleet-ai-textgen-panel";
describe("FleetAiTextgenPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiTextgenPanel services={5} active={5} generations={10000000} tokens={2000000000} />);
    expect(container.textContent).toContain("AI Text Gen");
}); });

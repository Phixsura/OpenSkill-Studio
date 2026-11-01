import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiStructPanel } from "@/components/fleet-ai-struct-panel";
describe("FleetAiStructPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiStructPanel services={5} active={5} generations={5000000} validationRate={99.5} />);
    expect(container.textContent).toContain("AI Structured Output");
}); });

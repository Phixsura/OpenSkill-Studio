import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiStructOutPanel } from "@/components/fleet-ai-struct-out-panel";
describe("FleetAiStructOutPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiStructOutPanel services={4} active={4} requests={8000000} validPct={99.9} schemas={300} />);
    expect(container.textContent).toContain("Structured Output");
}); });

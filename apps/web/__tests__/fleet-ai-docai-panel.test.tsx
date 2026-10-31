import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDocaiPanel } from "@/components/fleet-ai-docai-panel";
describe("FleetAiDocaiPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiDocaiPanel services={5} active={5} pages={25000000} fields={250000000} />);
    expect(container.textContent).toContain("AI Document");
}); });

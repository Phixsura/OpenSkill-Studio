import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiRecPanel } from "@/components/fleet-ai-rec-panel";
describe("FleetAiRecPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiRecPanel services={5} active={5} recs={50000000} ctr={10} />);
    expect(container.textContent).toContain("AI Recommendations");
}); });

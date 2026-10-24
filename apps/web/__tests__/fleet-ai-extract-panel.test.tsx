import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiExtractPanel } from "@/components/fleet-ai-extract-panel";
describe("FleetAiExtractPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiExtractPanel services={5} active={5} docs={2000000} entities={20000000} />);
    expect(container.textContent).toContain("AI Extraction");
}); });

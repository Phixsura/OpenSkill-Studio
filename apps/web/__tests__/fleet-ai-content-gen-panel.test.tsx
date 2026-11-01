import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiContentGenPanel } from "@/components/fleet-ai-content-gen-panel";
describe("FleetAiContentGenPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiContentGenPanel generators={4} active={4} content={2000000} words={200000000} quality={95} />);
    expect(container.textContent).toContain("Content Generator");
}); });

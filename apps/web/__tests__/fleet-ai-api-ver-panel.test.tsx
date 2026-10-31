import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiApiVerPanel } from "@/components/fleet-ai-api-ver-panel";
describe("FleetAiApiVerPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiApiVerPanel versioners={3} active={3} apis={200} versions={600} deprecated={100} />);
    expect(container.textContent).toContain("API Versioner");
}); });

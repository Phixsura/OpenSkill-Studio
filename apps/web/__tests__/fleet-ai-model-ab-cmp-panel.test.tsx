import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelAbCmpPanel } from "@/components/fleet-ai-model-ab-cmp-panel";
describe("FleetAiModelAbCmpPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelAbCmpPanel comparators={3} active={3} comparisons={500000} winners={400000} ties={100000} />);
    expect(container.textContent).toContain("A/B Compare");
}); });

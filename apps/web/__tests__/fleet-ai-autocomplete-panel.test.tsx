import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiAutocompletePanel } from "@/components/fleet-ai-autocomplete-panel";
describe("FleetAiAutocompletePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiAutocompletePanel engines={5} active={5} completions={200000000} acceptanceRate={45} latency={30} />);
    expect(container.textContent).toContain("Auto-Complete");
}); });

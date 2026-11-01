import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMistralPanel } from "@/components/fleet-mistral-panel";
describe("FleetMistralPanel", () => { it("renders", () => {
    const { container } = render(<FleetMistralPanel deployments={3} active={3} completions={6000000} tokens={3000000000} />);
    expect(container.textContent).toContain("Mistral");
}); });

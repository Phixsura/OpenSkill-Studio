import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCoherePanel } from "@/components/fleet-cohere-panel";
describe("FleetCoherePanel", () => { it("renders", () => {
    const { container } = render(<FleetCoherePanel endpoints={5} active={5} embedCalls={20000000} generateCalls={5000000} />);
    expect(container.textContent).toContain("Cohere");
}); });

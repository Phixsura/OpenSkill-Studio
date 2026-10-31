import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiInnovationV8Panel } from "@/components/fleet-ai-innovation-v8-panel";
describe("FleetAiInnovationV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiInnovationV8Panel trackers={3} active={3} experiments={10000} breakthroughs={200} patents={500} />);
    expect(container.textContent).toContain("Innovation v8");
}); });

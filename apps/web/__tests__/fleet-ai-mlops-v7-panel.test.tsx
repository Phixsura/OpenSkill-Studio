import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiMlopsV7Panel } from "@/components/fleet-ai-mlops-v7-panel";
describe("FleetAiMlopsV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiMlopsV7Panel systems={5} active={5} modelsProd={1000} experiments={5000} deploys={500} health={99} />);
    expect(container.textContent).toContain("MLOps v7");
}); });

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCicdV7Panel } from "@/components/fleet-ai-cicd-v7-panel";
describe("FleetAiCicdV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiCicdV7Panel pipelines={5} active={5} builds={10000} deploys={2000} passRate={99.8} duration={3} />);
    expect(container.textContent).toContain("CI/CD v7");
}); });

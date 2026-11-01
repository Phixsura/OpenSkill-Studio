import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCicdV8Panel } from "@/components/fleet-ai-cicd-v8-panel";
describe("FleetAiCicdV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiCicdV8Panel pipelines={5} active={5} builds={50000} deploys={5000} passRate={99.9} />);
    expect(container.textContent).toContain("CI/CD v8");
}); });

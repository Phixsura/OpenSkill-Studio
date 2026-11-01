import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCicdPanel } from "@/components/fleet-ai-cicd-panel";
describe("FleetAiCicdPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiCicdPanel pipelines={6} active={6} builds={1000} deploys={200} successRate={99} />);
    expect(container.textContent).toContain("AI CI/CD");
}); });

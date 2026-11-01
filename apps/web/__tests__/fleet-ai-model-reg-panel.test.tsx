import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelRegPanel } from "@/components/fleet-ai-model-reg-panel";
describe("FleetAiModelRegPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelRegPanel registries={3} active={3} models={100} versions={500} deployed={80} coverage={80.0} />);
    expect(container.textContent).toContain("Model Registry");
}); });

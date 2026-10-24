import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelRegV3Panel } from "@/components/fleet-ai-model-reg-v3-panel";
describe("FleetAiModelRegV3Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelRegV3Panel registries={3} active={3} models={2000} versions={20000} deployments={1000} tags={10000} />);
    expect(container.textContent).toContain("Model Registry v3");
}); });

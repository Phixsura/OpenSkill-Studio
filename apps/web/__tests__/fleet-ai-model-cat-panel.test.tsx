import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiModelCatPanel } from "@/components/fleet-ai-model-cat-panel";
describe("FleetAiModelCatPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiModelCatPanel catalogs={2} active={2} models={1000} providers={30} deployments={500} />);
    expect(container.textContent).toContain("Model Catalog");
}); });

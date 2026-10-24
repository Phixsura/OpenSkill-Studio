import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiMlopsV8Panel } from "@/components/fleet-ai-mlops-v8-panel";
describe("FleetAiMlopsV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiMlopsV8Panel systems={5} active={5} models={5000} experiments={20000} deploys={2000} health={99.5} />);
    expect(container.textContent).toContain("MLOps v8");
}); });

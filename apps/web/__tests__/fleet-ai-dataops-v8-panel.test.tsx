import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiDataopsV8Panel } from "@/components/fleet-ai-dataops-v8-panel";
describe("FleetAiDataopsV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiDataopsV8Panel systems={4} active={4} pipelines={2000} datasets={100000} quality={99.5} />);
    expect(container.textContent).toContain("DataOps v8");
}); });

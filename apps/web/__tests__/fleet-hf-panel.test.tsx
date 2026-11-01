import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetHfPanel } from "@/components/fleet-hf-panel";
describe("FleetHfPanel", () => { it("renders", () => {
    const { container } = render(<FleetHfPanel spaces={10} running={10} models={100} inferences={15000000} />);
    expect(container.textContent).toContain("Hugging Face");
}); });

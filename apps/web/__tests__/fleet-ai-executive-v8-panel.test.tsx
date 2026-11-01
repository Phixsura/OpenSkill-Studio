import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiExecutiveV8Panel } from "@/components/fleet-ai-executive-v8-panel";
describe("FleetAiExecutiveV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiExecutiveV8Panel />);
    expect(container.textContent).toContain("Executive v8");
    expect(container.textContent).toContain("NEVER STOPS");
}); });

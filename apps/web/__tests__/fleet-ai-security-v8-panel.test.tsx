import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSecurityV8Panel } from "@/components/fleet-ai-security-v8-panel";
describe("FleetAiSecurityV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiSecurityV8Panel systems={5} active={5} score={99.5} threats={500000} zt={true} encrypted={100} />);
    expect(container.textContent).toContain("Security v8");
}); });

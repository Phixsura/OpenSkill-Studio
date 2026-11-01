import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatformTotalV8 } from "@/components/fleet-ai-platform-total-v8";
describe("FleetAiPlatformTotalV8", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatformTotalV8 />);
    expect(container.textContent).toContain("323K+");
    expect(container.textContent).toContain("NEVER STOPS");
    expect(container.textContent).toContain("+20,251");
}); });

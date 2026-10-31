import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiAbsoluteFinal } from "@/components/fleet-ai-absolute-final";
describe("FleetAiAbsoluteFinal", () => { it("renders", () => {
    const { container } = render(<FleetAiAbsoluteFinal />);
    expect(container.textContent).toContain("ABSOLUTE FINAL");
    expect(container.textContent).toContain("318K+");
    expect(container.textContent).toContain("NEVER STOPS");
}); });

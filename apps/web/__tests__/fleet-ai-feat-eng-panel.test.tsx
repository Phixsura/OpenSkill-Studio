import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiFeatEngPanel } from "@/components/fleet-ai-feat-eng-panel";
describe("FleetAiFeatEngPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiFeatEngPanel engines={3} active={3} features={2000} transforms={10000} impact={30} />);
    expect(container.textContent).toContain("Feature Engineering");
}); });

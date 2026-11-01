import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAuthCovPanel } from "@/components/fleet-auth-cov-panel";
describe("FleetAuthCovPanel", () => { it("renders", () => {
    const { container } = render(<FleetAuthCovPanel total={20} authenticated={18} publicCount={2} fullyProtected={false} />);
    expect(container.textContent).toContain("Auth Coverage");
    expect(container.textContent).toContain("2 public");
}); });

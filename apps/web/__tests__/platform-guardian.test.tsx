import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformGuardian } from "@/components/platform-guardian";
describe("PlatformGuardian", () => { it("renders", () => {
    const { container } = render(<PlatformGuardian />);
    expect(container.textContent).toContain("GUARDIAN");
    expect(container.textContent).toContain("ALL CLEAR");
    expect(container.textContent).toContain("NEVER STOPS");
}); });

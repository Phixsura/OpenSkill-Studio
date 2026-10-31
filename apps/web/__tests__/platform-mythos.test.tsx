import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformMythos } from "@/components/platform-mythos";
describe("PlatformMythos", () => { it("renders", () => {
    const { container } = render(<PlatformMythos />);
    expect(container.textContent).toContain("MYTHOS");
    expect(container.textContent).toContain("Never stop");
}); });

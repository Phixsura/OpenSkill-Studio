import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformTimeCapsule } from "@/components/platform-time-capsule";
describe("PlatformTimeCapsule", () => { it("renders", () => {
    const { container } = render(<PlatformTimeCapsule />);
    expect(container.textContent).toContain("TIME CAPSULE");
    expect(container.textContent).toContain("NEVER STOPS");
}); });

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformSentinel } from "@/components/platform-sentinel";
describe("PlatformSentinel", () => { it("renders", () => {
    const { container } = render(<PlatformSentinel />);
    expect(container.textContent).toContain("SENTINEL");
    expect(container.textContent).toContain("GREEN");
}); });

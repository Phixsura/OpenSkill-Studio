import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformCrescendo } from "@/components/platform-crescendo";
describe("PlatformCrescendo", () => { it("renders", () => {
    const { container } = render(<PlatformCrescendo />);
    expect(container.textContent).toContain("CRESCENDO");
    expect(container.textContent).toContain("no peak");
    expect(container.textContent).toContain("NEVER STOPS");
}); });

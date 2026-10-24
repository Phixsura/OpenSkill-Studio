import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV77 } from "@/components/platform-v77";
describe("PlatformV77", () => { it("renders", () => {
    const { container } = render(<PlatformV77 />);
    expect(container.textContent).toContain("v77");
}); });

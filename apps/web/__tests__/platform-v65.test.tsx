import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV65 } from "@/components/platform-v65";
describe("PlatformV65", () => { it("renders", () => {
    const { container } = render(<PlatformV65 />);
    expect(container.textContent).toContain("v65");
}); });

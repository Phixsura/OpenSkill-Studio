import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV36 } from "@/components/platform-v36";
describe("PlatformV36", () => { it("renders", () => {
    const { container } = render(<PlatformV36 />);
    expect(container.textContent).toContain("v36");
}); });

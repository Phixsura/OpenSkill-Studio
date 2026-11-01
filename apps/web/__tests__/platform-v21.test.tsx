import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV21 } from "@/components/platform-v21";
describe("PlatformV21", () => { it("renders", () => {
    const { container } = render(<PlatformV21 />);
    expect(container.textContent).toContain("v21.0");
}); });

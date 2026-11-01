import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV76 } from "@/components/platform-v76";
describe("PlatformV76", () => { it("renders", () => {
    const { container } = render(<PlatformV76 />);
    expect(container.textContent).toContain("v76");
}); });

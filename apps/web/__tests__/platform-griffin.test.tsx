import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformGriffin } from "@/components/platform-griffin";
describe("PlatformGriffin", () => { it("renders", () => {
    const { container } = render(<PlatformGriffin />);
    expect(container.textContent).toContain("GRIFFIN");
    expect(container.textContent).toContain("Eagle");
    expect(container.textContent).toContain("Lion");
}); });

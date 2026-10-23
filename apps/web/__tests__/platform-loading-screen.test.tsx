import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UplatformUloadingUscreen } from "@/components/platform-loading-screen";

describe("UplatformUloadingUscreen", () => {
  it("renders", () => {
    const { container } = render(<UplatformUloadingUscreen status="operational" />);
    expect(container.textContent).toContain("operational");
  });
});

import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UplatformUerrorUpage } from "@/components/platform-error-page";

describe("UplatformUerrorUpage", () => {
  it("renders", () => {
    const { container } = render(<UplatformUerrorUpage status="operational" />);
    expect(container.textContent).toContain("operational");
  });
});

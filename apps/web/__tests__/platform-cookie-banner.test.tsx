import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UplatformUcookieUbanner } from "@/components/platform-cookie-banner";

describe("UplatformUcookieUbanner", () => {
  it("renders", () => {
    const { container } = render(<UplatformUcookieUbanner status="operational" />);
    expect(container.textContent).toContain("operational");
  });
});

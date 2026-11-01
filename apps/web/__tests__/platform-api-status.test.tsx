import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UplatformUapiUstatus } from "@/components/platform-api-status";

describe("UplatformUapiUstatus", () => {
  it("renders", () => {
    const { container } = render(<UplatformUapiUstatus status="operational" />);
    expect(container.textContent).toContain("operational");
  });
});

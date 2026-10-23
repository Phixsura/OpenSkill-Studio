import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { UplatformUannouncementUbar } from "@/components/platform-announcement-bar";

describe("UplatformUannouncementUbar", () => {
  it("renders", () => {
    const { container } = render(<UplatformUannouncementUbar status="operational" />);
    expect(container.textContent).toContain("operational");
  });
});

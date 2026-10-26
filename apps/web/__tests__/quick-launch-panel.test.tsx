import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { QuickLaunchPanel } from "@/components/quick-launch-panel";

const liveLaunch = {
  launchId: "ql-1", templateName: "slack-bot", extensionName: "my-bot",
  status: "live", progressPct: 100, previewUrl: "https://preview.openskill.dev/my-bot", error: "",
};

describe("QuickLaunchPanel", () => {
  it("shows launch button when empty", () => {
    const fn = vi.fn();
    const { getByText } = render(<QuickLaunchPanel launch={null} onLaunch={fn} />);
    fireEvent.click(getByText("Launch Now"));
    expect(fn).toHaveBeenCalled();
  });
  it("shows live launch with preview", () => {
    const { container } = render(<QuickLaunchPanel launch={liveLaunch} />);
    expect(container.textContent).toContain("my-bot");
    expect(container.textContent).toContain("100%");
    expect(container.textContent).toContain("preview.openskill.dev");
  });
});

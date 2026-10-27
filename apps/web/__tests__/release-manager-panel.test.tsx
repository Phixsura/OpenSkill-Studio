import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ReleaseManagerPanel } from "@/components/release-manager-panel";

const releases = [
  { releaseId: "r1", version: "2.0.0", status: "approved", changelog: ["New feature"], reviewComment: "Looks good!" },
  { releaseId: "r2", version: "1.5.0", status: "published", changelog: ["Bug fix"], reviewComment: "" },
];

describe("ReleaseManagerPanel", () => {
  it("renders releases", () => {
    const { container } = render(<ReleaseManagerPanel releases={releases} />);
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("Approved");
    expect(container.textContent).toContain("Looks good!");
    expect(container.textContent).toContain("Publish");
  });
  it("publish release", () => {
    const fn = vi.fn();
    const { container } = render(<ReleaseManagerPanel releases={releases} onPublish={fn} />);
    const publishBtn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Publish");
    if (publishBtn) fireEvent.click(publishBtn);
    expect(fn).toHaveBeenCalledWith("r1");
  });
});

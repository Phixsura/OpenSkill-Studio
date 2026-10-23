import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AnnouncementBanner } from "@/components/announcement-banner";

describe("AnnouncementBanner", () => {
  it("renders banners", () => {
    const onDismiss = vi.fn();
    const { container, getAllByText } = render(
      <AnnouncementBanner onDismiss={onDismiss} announcements={[
        { id: "a1", title: "New Feature!", body: "SSO support", variant: "success", link: "", dismissible: true },
        { id: "a2", title: "Maintenance", body: "Scheduled", variant: "warning", link: "", dismissible: true },
      ]} />
    );
    expect(container.textContent).toContain("New Feature!");
    expect(container.textContent).toContain("SSO support");
    expect(container.textContent).toContain("Maintenance");
    fireEvent.click(getAllByText("✕")[0]);
    expect(onDismiss).toHaveBeenCalledWith("a1");
  });
});

import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { FeatureAnnouncementCard } from "@/components/feature-announcement-card";

describe("FeatureAnnouncementCard", () => {
  const announcements = [{
    announcement_id: "a1", title: "Dark Mode", body: "Now available!",
    feature_tag: "ui", cta: { label: "Try it", url: "/settings" }, published_at: "2026-10-23",
  }];
  it("renders", () => {
    const { container } = render(
      <FeatureAnnouncementCard announcements={announcements} onDismiss={vi.fn()} onCtaClick={vi.fn()} />
    );
    expect(container.textContent).toContain("What's New");
    expect(container.textContent).toContain("Dark Mode");
    expect(container.textContent).toContain("Now available!");
    expect(container.textContent).toContain("Try it");
  });
  it("cta click", () => {
    const fn = vi.fn();
    const { container } = render(
      <FeatureAnnouncementCard announcements={announcements} onDismiss={vi.fn()} onCtaClick={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Try it")!);
    expect(fn).toHaveBeenCalledWith("/settings");
  });
});

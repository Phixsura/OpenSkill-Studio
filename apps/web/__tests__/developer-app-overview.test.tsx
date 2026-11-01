import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DeveloperAppOverview } from "@/components/developer-app-overview";

const MOCK_STATS = {
  total_installs: 1500,
  active_installs: 890,
  avg_rating: 4.6,
  total_reviews: 42,
  api_calls_today: 7500,
  api_calls_limit: 10000,
  webhook_success_rate: 98,
  sandbox_executions_today: 23,
};

const MOCK_VERSIONS = [
  { version: "2.1.0", status: "published" as const, created_at: "2026-10-25" },
  { version: "2.0.0", status: "published" as const, created_at: "2026-10-10" },
  { version: "1.9.0", status: "rejected" as const, created_at: "2026-10-05" },
];

const defaultProps = {
  appId: "app-1",
  appName: "LMS Connector",
  appIcon: "🔗",
  status: "published" as const,
  description: "Sync courses and grades with your LMS",
  category: "connector",
  stats: MOCK_STATS,
  versions: MOCK_VERSIONS,
  onPublish: vi.fn(),
  onViewAnalytics: vi.fn(),
  onManageVersions: vi.fn(),
};

describe("DeveloperAppOverview", () => {
  it("renders app name and icon", () => {
    const { container } = render(<DeveloperAppOverview {...defaultProps} />);
    expect(container.textContent).toContain("LMS Connector");
    expect(container.textContent).toContain("🔗");
  });

  it("renders status badge", () => {
    const { container } = render(<DeveloperAppOverview {...defaultProps} />);
    expect(container.textContent).toContain("Published");
  });

  it("renders category and description", () => {
    const { container } = render(<DeveloperAppOverview {...defaultProps} />);
    expect(container.textContent).toContain("connector");
    expect(container.textContent).toContain("Sync courses and grades");
  });

  it("renders install stats", () => {
    const { container } = render(<DeveloperAppOverview {...defaultProps} />);
    expect(container.textContent).toContain("890");
    expect(container.textContent).toContain("1,500 total");
  });

  it("renders rating", () => {
    const { container } = render(<DeveloperAppOverview {...defaultProps} />);
    expect(container.textContent).toContain("4.6");
    expect(container.textContent).toContain("42 reviews");
  });

  it("renders API usage", () => {
    const { container } = render(<DeveloperAppOverview {...defaultProps} />);
    expect(container.textContent).toContain("7,500");
    expect(container.textContent).toContain("10,000");
    expect(container.textContent).toContain("75% of limit");
  });

  it("renders webhook success rate", () => {
    const { container } = render(<DeveloperAppOverview {...defaultProps} />);
    expect(container.textContent).toContain("98%");
  });

  it("renders versions list", () => {
    const { container } = render(<DeveloperAppOverview {...defaultProps} />);
    expect(container.textContent).toContain("2.1.0");
    expect(container.textContent).toContain("2.0.0");
    expect(container.textContent).toContain("1.9.0");
    expect(container.textContent).toContain("rejected");
  });

  it("shows Submit for Review for draft apps", () => {
    const onPublish = vi.fn();
    const { container } = render(
      <DeveloperAppOverview {...defaultProps} status="draft" onPublish={onPublish} />,
    );
    const btn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Submit for Review",
    );
    expect(btn).toBeTruthy();
    fireEvent.click(btn!);
    expect(onPublish).toHaveBeenCalledOnce();
  });

  it("hides Submit for Review for published apps", () => {
    const { container } = render(<DeveloperAppOverview {...defaultProps} />);
    const btn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Submit for Review",
    );
    expect(btn).toBeFalsy();
  });

  it("calls onViewAnalytics", () => {
    const onViewAnalytics = vi.fn();
    const { container } = render(
      <DeveloperAppOverview {...defaultProps} onViewAnalytics={onViewAnalytics} />,
    );
    const btn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Analytics",
    );
    fireEvent.click(btn!);
    expect(onViewAnalytics).toHaveBeenCalledOnce();
  });

  it("calls onManageVersions", () => {
    const onManageVersions = vi.fn();
    const { container } = render(
      <DeveloperAppOverview {...defaultProps} onManageVersions={onManageVersions} />,
    );
    const btn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Manage",
    );
    fireEvent.click(btn!);
    expect(onManageVersions).toHaveBeenCalledOnce();
  });

  it("shows empty versions state", () => {
    const { container } = render(<DeveloperAppOverview {...defaultProps} versions={[]} />);
    expect(container.textContent).toContain("No versions yet");
  });

  it("renders suspended badge", () => {
    const { container } = render(<DeveloperAppOverview {...defaultProps} status="suspended" />);
    expect(container.textContent).toContain("Suspended");
  });
});

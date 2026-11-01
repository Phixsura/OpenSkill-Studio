import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppPermissionReview } from "@/components/app-permission-review";

const MOCK_SCAN = {
  permissions: [
    {
      scope: "read:skills",
      risk: "low" as const,
      category: "content",
      description: "View skills and categories",
      requires_review: false,
    },
    {
      scope: "write:projects",
      risk: "medium" as const,
      category: "content",
      description: "Create and update projects",
      requires_review: false,
    },
    {
      scope: "read:email",
      risk: "high" as const,
      category: "identity",
      description: "View user email address",
      requires_review: true,
    },
    {
      scope: "admin:org",
      risk: "critical" as const,
      category: "admin",
      description: "Full organization admin access",
      requires_review: true,
    },
  ],
  total_scopes: 4,
  trust_score: 53,
  warnings: ["App requests both admin and delete access — review carefully"],
  requires_human_review: true,
  human_summary:
    "This app accesses: 2 content permissions, identity (read:email), admin (admin:org). ⚠️ Includes 1 critical-level permission(s).",
};

const SAFE_SCAN = {
  permissions: [
    {
      scope: "read:skills",
      risk: "low" as const,
      category: "content",
      description: "View skills",
      requires_review: false,
    },
  ],
  total_scopes: 1,
  trust_score: 98,
  warnings: [],
  requires_human_review: false,
  human_summary: "This app accesses: content (read:skills).",
};

describe("AppPermissionReview", () => {
  it("renders app name and scope count", () => {
    const { container } = render(
      <AppPermissionReview
        appName="Test App"
        scanResult={MOCK_SCAN}
        onApprove={vi.fn()}
        onReject={vi.fn()}
      />,
    );
    expect(container.textContent).toContain("Test App");
    expect(container.textContent).toContain("4 permissions");
  });

  it("renders trust score", () => {
    const { container } = render(
      <AppPermissionReview
        appName="Test App"
        scanResult={MOCK_SCAN}
        onApprove={vi.fn()}
        onReject={vi.fn()}
      />,
    );
    expect(container.textContent).toContain("53");
  });

  it("renders human summary", () => {
    const { container } = render(
      <AppPermissionReview
        appName="Test App"
        scanResult={MOCK_SCAN}
        onApprove={vi.fn()}
        onReject={vi.fn()}
      />,
    );
    expect(container.textContent).toContain("critical-level");
  });

  it("renders warnings when present", () => {
    const { container } = render(
      <AppPermissionReview
        appName="Test App"
        scanResult={MOCK_SCAN}
        onApprove={vi.fn()}
        onReject={vi.fn()}
      />,
    );
    expect(container.textContent).toContain("Warnings");
    expect(container.textContent).toContain("review carefully");
  });

  it("hides warnings section when empty", () => {
    const { container } = render(
      <AppPermissionReview
        appName="Safe App"
        scanResult={SAFE_SCAN}
        onApprove={vi.fn()}
        onReject={vi.fn()}
      />,
    );
    expect(container.textContent).not.toContain("Warnings");
  });

  it("renders permission scopes with risk badges", () => {
    const { container } = render(
      <AppPermissionReview
        appName="Test App"
        scanResult={MOCK_SCAN}
        onApprove={vi.fn()}
        onReject={vi.fn()}
      />,
    );
    expect(container.textContent).toContain("read:skills");
    expect(container.textContent).toContain("Low");
    expect(container.textContent).toContain("admin:org");
    expect(container.textContent).toContain("Critical");
  });

  it("groups permissions by category", () => {
    const { container } = render(
      <AppPermissionReview
        appName="Test App"
        scanResult={MOCK_SCAN}
        onApprove={vi.fn()}
        onReject={vi.fn()}
      />,
    );
    expect(container.textContent).toContain("content");
    expect(container.textContent).toContain("identity");
    expect(container.textContent).toContain("admin");
  });

  it("shows requires review for flagged permissions", () => {
    const { container } = render(
      <AppPermissionReview
        appName="Test App"
        scanResult={MOCK_SCAN}
        onApprove={vi.fn()}
        onReject={vi.fn()}
      />,
    );
    expect(container.textContent).toContain("requires review");
  });

  it("shows human review notice when required", () => {
    const { container } = render(
      <AppPermissionReview
        appName="Test App"
        scanResult={MOCK_SCAN}
        onApprove={vi.fn()}
        onReject={vi.fn()}
      />,
    );
    expect(container.textContent).toContain("Requires human review");
  });

  it("hides human review notice when not required", () => {
    const { container } = render(
      <AppPermissionReview
        appName="Safe App"
        scanResult={SAFE_SCAN}
        onApprove={vi.fn()}
        onReject={vi.fn()}
      />,
    );
    expect(container.textContent).not.toContain("Requires human review");
  });

  it("calls onApprove when Approve clicked", () => {
    const onApprove = vi.fn();
    const { container } = render(
      <AppPermissionReview
        appName="Test App"
        scanResult={MOCK_SCAN}
        onApprove={onApprove}
        onReject={vi.fn()}
      />,
    );
    const btn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Approve",
    );
    fireEvent.click(btn!);
    expect(onApprove).toHaveBeenCalledOnce();
  });

  it("calls onReject when Reject clicked", () => {
    const onReject = vi.fn();
    const { container } = render(
      <AppPermissionReview
        appName="Test App"
        scanResult={MOCK_SCAN}
        onApprove={vi.fn()}
        onReject={onReject}
      />,
    );
    const btn = Array.from(container.querySelectorAll("button")).find(
      (b) => b.textContent === "Reject",
    );
    fireEvent.click(btn!);
    expect(onReject).toHaveBeenCalledOnce();
  });

  it("renders permission descriptions", () => {
    const { container } = render(
      <AppPermissionReview
        appName="Test App"
        scanResult={MOCK_SCAN}
        onApprove={vi.fn()}
        onReject={vi.fn()}
      />,
    );
    expect(container.textContent).toContain("View skills and categories");
    expect(container.textContent).toContain("Full organization admin access");
  });

  it("handles singular permission count", () => {
    const { container } = render(
      <AppPermissionReview
        appName="Safe App"
        scanResult={SAFE_SCAN}
        onApprove={vi.fn()}
        onReject={vi.fn()}
      />,
    );
    expect(container.textContent).toContain("1 permission");
    expect(container.textContent).not.toContain("1 permissions");
  });
});

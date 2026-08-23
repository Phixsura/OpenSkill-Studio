import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";

vi.mock("@/lib/api", () => ({
  apiWithAuth: vi.fn(),
  ApiError: class extends Error {},
}));

import { NotificationBell } from "@/components/notification-bell";
import { apiWithAuth } from "@/lib/api";

const mockApiWithAuth = vi.mocked(apiWithAuth);

function createWrapper() {
  const qc = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={qc}>{children}</QueryClientProvider>
  );
}

describe("NotificationBell", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders bell button with aria-label", () => {
    mockApiWithAuth.mockResolvedValue({ data: [] });
    render(<NotificationBell />, { wrapper: createWrapper() });
    const button = screen.getByRole("button", { name: /notifications/i });
    expect(button).toBeDefined();
    expect(button.getAttribute("aria-expanded")).toBe("false");
  });

  it("shows unread count badge", async () => {
    mockApiWithAuth.mockResolvedValue({
      data: [
        { id: "n1", title: "Update available", body: null, is_read: false, created_at: "2026-08-20T10:00:00Z" },
        { id: "n2", title: "Review posted", body: "Great!", is_read: false, created_at: "2026-08-20T09:00:00Z" },
      ],
    });
    render(<NotificationBell />, { wrapper: createWrapper() });
    expect(await screen.findByText("2")).toBeDefined();
  });

  it("does not show badge when all read", async () => {
    mockApiWithAuth.mockResolvedValue({
      data: [
        { id: "n1", title: "Old news", body: null, is_read: true, created_at: "2026-08-20T10:00:00Z" },
      ],
    });
    render(<NotificationBell />, { wrapper: createWrapper() });
    // Wait for query to settle
    await screen.findByRole("button", { name: /notifications/i });
    // No badge should be present (badge only renders when unreadCount > 0)
    expect(screen.queryByText("1")).toBeNull();
  });

  it("toggles dropdown on click", async () => {
    mockApiWithAuth.mockResolvedValue({
      data: [
        { id: "n1", title: "New pack version", body: "Check it out", is_read: false, created_at: "2026-08-20T10:00:00Z" },
      ],
    });
    render(<NotificationBell />, { wrapper: createWrapper() });
    const button = await screen.findByRole("button", { name: /notifications/i });

    // Dropdown should not be visible initially
    expect(screen.queryByText("Notifications")).toBeNull();

    // Click to open
    fireEvent.click(button);
    expect(screen.getByText("Notifications")).toBeDefined();
    expect(button.getAttribute("aria-expanded")).toBe("true");

    // Click again to close
    fireEvent.click(button);
    expect(screen.queryByText("Notifications")).toBeNull();
    expect(button.getAttribute("aria-expanded")).toBe("false");
  });

  it("displays notification items when open", async () => {
    mockApiWithAuth.mockResolvedValue({
      data: [
        { id: "n1", title: "Pack Update", body: "New version 2.0", is_read: false, created_at: "2026-08-20T10:00:00Z" },
        { id: "n2", title: "Review Added", body: null, is_read: true, created_at: "2026-08-19T10:00:00Z" },
      ],
    });
    render(<NotificationBell />, { wrapper: createWrapper() });
    const button = await screen.findByRole("button", { name: /notifications/i });
    fireEvent.click(button);

    expect(screen.getByText("Pack Update")).toBeDefined();
    expect(screen.getByText("New version 2.0")).toBeDefined();
    expect(screen.getByText("Review Added")).toBeDefined();
  });

  it("shows mark-read button for unread notifications", async () => {
    mockApiWithAuth.mockResolvedValue({
      data: [
        { id: "n1", title: "Unread One", body: null, is_read: false, created_at: "2026-08-20T10:00:00Z" },
      ],
    });
    render(<NotificationBell />, { wrapper: createWrapper() });
    const button = await screen.findByRole("button", { name: /notifications/i });
    fireEvent.click(button);

    expect(screen.getByText("Mark read")).toBeDefined();
    expect(screen.getByText("Mark all read")).toBeDefined();
  });

  it("shows empty state when no notifications", async () => {
    mockApiWithAuth.mockResolvedValue({ data: [] });
    render(<NotificationBell />, { wrapper: createWrapper() });
    const button = await screen.findByRole("button", { name: /notifications/i });
    fireEvent.click(button);

    expect(screen.getByText("No notifications")).toBeDefined();
    // Mark all read should NOT appear when no unread
    expect(screen.queryByText("Mark all read")).toBeNull();
  });
});

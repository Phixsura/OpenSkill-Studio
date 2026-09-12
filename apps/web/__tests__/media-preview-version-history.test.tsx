import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/components/lightbox", () => ({
  Lightbox: () => <div data-testid="lightbox" />,
}));
const toasts = vi.hoisted(() => ({ error: vi.fn(), success: vi.fn() }));
vi.mock("sonner", () => ({ toast: toasts }));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import { MediaPreview } from "@/components/media-preview";
import { VersionHistory } from "@/components/version-history";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

beforeEach(() => {
  vi.clearAllMocks();
  api.mockResolvedValue({ download_url: "https://cdn.example/file" });
});

describe("MediaPreview (R506) — §30 media playback element selection", () => {
  const base = { downloadPath: "/dl", fileName: "work.bin" };

  it("image → <img> with lightbox; video → <video controls>; audio → <audio controls>; other → download link", async () => {
    const img = render(<MediaPreview {...base} mimeType="image/png" />);
    const el = await screen.findByAltText("work.bin");
    expect(el.tagName).toBe("IMG");
    fireEvent.click(el);
    expect(screen.getByTestId("lightbox")).toBeTruthy();
    img.unmount();

    const vid = render(<MediaPreview {...base} mimeType="video/mp4" />);
    await waitFor(() => expect(document.querySelector("video")).toBeTruthy());
    expect(document.querySelector("video")?.getAttribute("controls")).not.toBeNull();
    vid.unmount();

    const aud = render(<MediaPreview {...base} mimeType="audio/mpeg" />);
    await waitFor(() => expect(document.querySelector("audio")).toBeTruthy());
    aud.unmount();

    const pdf = render(<MediaPreview {...base} mimeType="application/pdf" />);
    const link = await screen.findByText(/work\.bin/);
    expect(link.closest("a")?.getAttribute("href")).toBe("https://cdn.example/file");
    expect(link.closest("a")?.getAttribute("rel")).toContain("noopener");
    pdf.unmount();
  });

  it("presign failure falls back to the unavailable notice, never a broken element", async () => {
    api.mockRejectedValue(new Error("403"));
    render(<MediaPreview {...base} mimeType="image/png" />);
    expect(await screen.findByText(/Preview unavailable — work\.bin/)).toBeTruthy();
    expect(document.querySelector("img")).toBeNull();
  });
});

describe("VersionHistory (R506) — §30 version list", () => {
  const ITEMS = [
    {
      id: "v1",
      version: 1,
      file_name: "hero-v1.png",
      mime_type: "image/png",
      note: null,
      created_at: "2026-09-01T00:00:00Z",
    },
    {
      id: "v3",
      version: 3,
      file_name: "hero-v3.png",
      mime_type: "image/png",
      note: "brighter sky",
      created_at: "2026-09-03T00:00:00Z",
    },
    {
      id: "v2",
      version: 2,
      file_name: "hero-v2.pdf",
      mime_type: "application/pdf",
      note: null,
      created_at: "2026-09-02T00:00:00Z",
    },
  ];
  const dl = (id: string) => `/files/${id}/download`;

  it("renders nothing for fewer than 2 versions", () => {
    const { container } = render(<VersionHistory items={[ITEMS[0]!]} downloadPath={dl} />);
    expect(container.textContent).toBe("");
  });

  it("expanded list sorts newest-first, tags only the newest as latest, shows the note, and presigns only image thumbs", async () => {
    render(<VersionHistory items={ITEMS} downloadPath={dl} />);
    fireEvent.click(screen.getByText(/Version history \(3\)/));
    await screen.findByText("v3");
    const body = document.body.textContent ?? "";
    // newest first: v3 before v2 before v1
    expect(body.indexOf("v3")).toBeLessThan(body.indexOf("v2"));
    expect(body.indexOf("v2")).toBeLessThan(body.indexOf("hero-v1.png"));
    // "latest" chip only on the row of the highest version
    const latestChips = screen.getAllByText("latest");
    expect(latestChips.length).toBe(1);
    expect(latestChips[0]?.closest("li")?.textContent).toContain("v3");
    expect(body).toContain("brighter sky"); // note rendered
    // presign requested for the two images only, not the pdf
    await waitFor(() => expect(api).toHaveBeenCalledTimes(2));
    const presigned = api.mock.calls.map((c) => String(c[0])).sort();
    expect(presigned).toEqual(["/files/v1/download", "/files/v3/download"]);
  });

  it("Download presigns the row's item and opens it; failure toasts", async () => {
    const open = vi.spyOn(window, "open").mockReturnValue(null);
    render(<VersionHistory items={ITEMS} downloadPath={dl} />);
    fireEvent.click(screen.getByText(/Version history/));
    await screen.findByText("v3");
    api.mockClear();
    api.mockResolvedValue({ download_url: "https://cdn.example/v2.pdf" });
    // v2 is the second row (newest-first)
    fireEvent.click(screen.getAllByRole("button", { name: "Download" })[1] as HTMLElement);
    await waitFor(() =>
      expect(open).toHaveBeenCalledWith("https://cdn.example/v2.pdf", "_blank", "noopener"),
    );
    expect(String(api.mock.calls[0]?.[0])).toBe("/files/v2/download");

    api.mockRejectedValue(new Error("410"));
    fireEvent.click(screen.getAllByRole("button", { name: "Download" })[0] as HTMLElement);
    await waitFor(() => expect(toasts.error).toHaveBeenCalled());
    open.mockRestore();
  });
});

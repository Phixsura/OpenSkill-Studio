import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/components/lightbox", () => ({
  Lightbox: ({ onClose }: { onClose: () => void }) => (
    <div data-testid="lightbox" onClick={onClose} />
  ),
}));
vi.mock("@/lib/api", () => ({ apiWithAuth: vi.fn(), ApiError: class extends Error {} }));

import { AnnotatedImage, type ItemComment } from "@/components/annotated-media";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function regionComment(
  id: string,
  bounds: Record<string, number>,
  over: Partial<ItemComment> = {},
) {
  return {
    id,
    item_id: "it-1",
    author_id: "u-1",
    author_name: "Ada",
    parent_id: null,
    text: `note ${id}`,
    anchor_type: "region",
    timestamp_ms: null,
    duration_ms: null,
    region: { type: "rectangle", bounds },
    completed: false,
    created_at: "2026-09-01T00:00:00Z",
    ...over,
  } as ItemComment;
}

const base = { downloadPath: "/orgs/o-1/submissions/s-1/files/it-1/download", comments: [] };

// deterministic 200x100 container for normalized math
const RECT = {
  left: 0,
  top: 0,
  width: 200,
  height: 100,
  right: 200,
  bottom: 100,
  x: 0,
  y: 0,
  toJSON: () => ({}),
} as DOMRect;

beforeEach(() => {
  vi.clearAllMocks();
  api.mockResolvedValue({ download_url: "https://cdn.example/img.png" });
  vi.spyOn(Element.prototype, "getBoundingClientRect").mockReturnValue(RECT);
});
afterEach(() => vi.restoreAllMocks());

async function renderReady(props: Record<string, unknown> = {}) {
  const utils = render(<AnnotatedImage {...base} {...props} />);
  await screen.findByTestId("annotated-image");
  return utils;
}

describe("AnnotatedImage (R505)", () => {
  it("drag in drawing mode emits a NORMALIZED rectangle with min/max ordering and 0-1 clamping", async () => {
    const onDraw = vi.fn();
    await renderReady({ drawing: true, onDrawRegion: onDraw });
    const box = screen.getByTestId("annotated-image");
    // drag from bottom-right to top-left, ending OUTSIDE the container
    fireEvent.mouseDown(box, { clientX: 150, clientY: 80 });
    fireEvent.mouseMove(box, { clientX: -50, clientY: 20 }); // x clamps to 0
    fireEvent.mouseUp(box);
    expect(onDraw).toHaveBeenCalledWith({
      type: "rectangle",
      bounds: { minX: 0, minY: 0.2, maxX: 0.75, maxY: 0.8 }, // reordered + clamped
    });
  });

  it("a tiny drag becomes a POINT annotation; no drawing outside drawing mode", async () => {
    const onDraw = vi.fn();
    const first = await renderReady({ drawing: true, onDrawRegion: onDraw });
    const box = screen.getByTestId("annotated-image");
    fireEvent.mouseDown(box, { clientX: 100, clientY: 50 });
    fireEvent.mouseMove(box, { clientX: 100.5, clientY: 50.2 });
    fireEvent.mouseUp(box);
    expect(onDraw).toHaveBeenCalledTimes(1);
    expect(onDraw.mock.calls[0]?.[0].type).toBe("point");
    first.unmount();

    onDraw.mockClear();
    await renderReady({ drawing: false, onDrawRegion: onDraw });
    const box2 = screen.getByTestId("annotated-image");
    fireEvent.mouseDown(box2, { clientX: 10, clientY: 10 });
    fireEvent.mouseMove(box2, { clientX: 100, clientY: 60 });
    fireEvent.mouseUp(box2);
    expect(onDraw).not.toHaveBeenCalled();
  });

  it("region pins are positioned by normalized bounds and numbered; click toggles selection", async () => {
    const onSelect = vi.fn();
    await renderReady({
      comments: [
        regionComment("c-a", { minX: 0.1, minY: 0.2, maxX: 0.5, maxY: 0.6 }),
        regionComment("c-b", { minX: 0.7, minY: 0.7, maxX: 0.9, maxY: 0.9 }),
      ],
      activeCommentId: "c-b",
      onSelectComment: onSelect,
    });
    const pin1 = screen.getByTestId("annotation-1");
    expect(pin1.style.left).toBe("10%");
    expect(pin1.style.top).toBe("20%");
    expect(pin1.style.width).toBe("40%"); // (0.5-0.1)*100
    expect(pin1.style.height).toBe("40%");
    // active pin styled blue, inactive amber
    expect(screen.getByTestId("annotation-2").className).toContain("border-blue-500");
    expect(pin1.className).toContain("border-amber-500");
    // clicking the ACTIVE pin deselects (null); clicking inactive selects it
    fireEvent.click(screen.getByTestId("annotation-2"));
    expect(onSelect).toHaveBeenCalledWith(null);
    fireEvent.click(pin1);
    expect(onSelect).toHaveBeenCalledWith("c-a");
  });

  it("click outside drawing mode opens the lightbox; download failure shows the fallback", async () => {
    const first = await renderReady({ fileName: "hero.png" });
    fireEvent.click(screen.getByAltText("hero.png"));
    expect(screen.getByTestId("lightbox")).toBeTruthy();
    first.unmount();

    vi.clearAllMocks();
    api.mockRejectedValue(new Error("403"));
    render(<AnnotatedImage {...base} fileName="hero.png" />);
    await waitFor(() => expect(screen.getByText(/Preview unavailable — hero.png/)).toBeTruthy());
  });
});

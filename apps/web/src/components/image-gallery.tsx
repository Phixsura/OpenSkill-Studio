"use client";

import { useState } from "react";

interface GalleryImage { src: string; alt: string; caption: string; }
interface ImageGalleryProps { images: GalleryImage[]; }

export function ImageGallery({ images }: ImageGalleryProps) {
  const [lightbox, setLightbox] = useState<number | null>(null);

  return (
    <>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        {images.map((img, i) => (
          <button key={i} onClick={() => setLightbox(i)} className="group overflow-hidden rounded-lg border dark:border-gray-700">
            <img src={img.src} alt={img.alt} className="aspect-video w-full object-cover transition group-hover:scale-105" />
            {img.caption && <p className="px-2 py-1.5 text-xs text-gray-500 truncate">{img.caption}</p>}
          </button>
        ))}
      </div>
      {lightbox !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80" onClick={() => setLightbox(null)}>
          <div className="relative max-h-[90vh] max-w-[90vw]" onClick={e => e.stopPropagation()}>
            <img src={images[lightbox].src} alt={images[lightbox].alt} className="max-h-[85vh] rounded-lg object-contain" />
            {images[lightbox].caption && <p className="mt-2 text-center text-sm text-white">{images[lightbox].caption}</p>}
            <button onClick={() => setLightbox(null)} className="absolute -top-3 -right-3 flex h-8 w-8 items-center justify-center rounded-full bg-white text-sm font-bold shadow dark:bg-gray-800">✕</button>
          </div>
        </div>
      )}
    </>
  );
}

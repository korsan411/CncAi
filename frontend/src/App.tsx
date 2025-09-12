import React, { useState, useRef } from "react";

export default function App() {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const url = URL.createObjectURL(file);
    setImageUrl(url);

    const img = new Image();
    img.src = url;
    img.onload = () => {
      const canvas = canvasRef.current;
      if (canvas) {
        const ctx = canvas.getContext("2d");
        if (ctx) {
          // نضبط حجم الكانفاس على حسب أبعاد الصورة
          canvas.width = img.width;
          canvas.height = img.height;

          // نرسم الصورة
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          ctx.drawImage(img, 0, 0);
        }
      }
    };
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-6 p-6 bg-gray-100">
      <h1 className="text-2xl font-bold">معاينة الصورة ورفعها</h1>

      <input
        type="file"
        accept="image/*"
        onChange={handleImageUpload}
        className="p-2 border rounded"
      />

      <canvas
        ref={canvasRef}
        className="border shadow-md rounded"
      />

      {imageUrl && (
        <p className="text-sm text-gray-600">
          الصورة معروضة بحجمها الأصلي ({canvasRef.current?.width}×
          {canvasRef.current?.height})
        </p>
      )}
    </div>
  );
}

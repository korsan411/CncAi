import useWebSocketProgress from "@/hooks/useWebSocketProgress";
import { useState, useRef } from "react";

export default function PreviewWithProgress({ imageUrl }: { imageUrl: string }) {
  const { progress, zipFile, gcodePreview, gcodeFull, gcodeTotalLines, setGcodePreview } = useWebSocketProgress();
  const [expanded, setExpanded] = useState(false);
  const [searchTerm, setSearchTerm] = useState(""); 
  const [foundLine, setFoundLine] = useState<number | null>(null);
  const gcodeRef = useRef<HTMLDivElement>(null);

  const handleExpand = () => {
    if (!expanded && gcodeFull) {
      setGcodePreview(gcodeFull.split("\n").slice(0, 500).join("\n"));
      setExpanded(true);
    } else if (expanded && gcodeFull) {
      setGcodePreview(gcodeFull);
      setExpanded(false);
    }
  };

  const handleSearch = () => {
    if (!gcodeFull || !searchTerm.trim()) return;
    const lines = gcodeFull.split("\n");

    const idx = lines.findIndex((line) => line.toLowerCase().includes(searchTerm.toLowerCase()));
    if (idx >= 0) {
      setFoundLine(idx);
      setTimeout(() => {
        if (gcodeRef.current) {
          const el = gcodeRef.current.querySelector(`[data-line="${idx}"]`);
          el && el.scrollIntoView({ behavior: "smooth", block: "center" });
        }
      }, 100);
    } else {
      alert("لم يتم العثور على المصطلح في G-code");
    }
  };

  const gcodeLines = gcodePreview
    ? gcodePreview.split("\n").map((line, i) => (
        <div key={i} data-line={i} style={{whiteSpace: "pre"}} className={foundLine===i ? "bg-yellow-600 text-white" : ""}>
          <span style={{color:"#9CA3AF"}}>{i+1}.</span> {line}
        </div>
      ))
    : [];

  return (
    <div>
      <div className="text-sm text-gray-700 mb-2">التقدم: {progress}%</div>
      <div className="mb-2">
        {zipFile && (
          <a href={URL.createObjectURL(zipFile)} download="multipass_gcode.zip" className="px-3 py-1 bg-blue-600 text-white rounded"
             onClick={(e)=>{ setTimeout(()=>{ try{ URL.revokeObjectURL((e.target as HTMLAnchorElement).href); }catch{} }, 5000); }}>
            تحميل ZIP
          </a>
        )}
      </div>

      <div className="flex justify-between items-center mb-2">
        <span className="text-gray-600 text-sm">سطر G-code: {gcodeTotalLines}</span>
        <div className="flex gap-2">
          <input type="text" placeholder="ابحث في G-code" value={searchTerm} onChange={(e)=>setSearchTerm(e.target.value)} className="border rounded px-2 py-1" />
          <button onClick={handleSearch} className="px-3 py-1 bg-blue-600 text-white rounded">بحث</button>
          <button onClick={()=>{ if (gcodePreview) { navigator.clipboard.writeText(gcodePreview); alert("تم نسخ جزء من G-code"); } }} className="px-3 py-1 bg-green-600 text-white rounded">
            نسخ المعاينة
          </button>
        </div>
      </div>

      <div ref={gcodeRef} className="bg-black text-green-400 font-mono p-3 rounded h-64 overflow-y-auto text-sm">
        {gcodeLines}
      </div>

      <button onClick={handleExpand} className="mt-2 px-3 py-1 bg-gray-700 text-white rounded">
        {expanded ? "تصغير المعاينة" : "توسيع المعاينة"}
      </button>
    </div>
  );
}

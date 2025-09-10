import { useEffect, useState, useRef } from "react";
import JSZip from "jszip";

export default function useWebSocketProgress() {
  const [progress, setProgress] = useState(0);
  const [zipFile, setZipFile] = useState<Blob | null>(null);
  const [gcodePreview, setGcodePreview] = useState<string>("");
  const [gcodeFull, setGcodeFull] = useState<string>("");
  const [gcodeTotalLines, setGcodeTotalLines] = useState<number>(0);
  const wsRef = useRef<WebSocket|null>(null);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/progress");
    ws.binaryType = "arraybuffer";
    wsRef.current = ws;

    ws.onmessage = async (ev) => {
      if (typeof ev.data === "string") {
        const msg = JSON.parse(ev.data);
        if (msg.event === "pass_start") setProgress((p) => Math.min(p + 15, 90));
        if (msg.event === "pass_done") setProgress((p) => Math.min(p + 10, 95));
        if (msg.event === "finishing") setProgress(100);
      } else {
        const blob = new Blob([ev.data], { type: "application/zip" });
        setZipFile(blob);
        const zip = await JSZip.loadAsync(blob);
        const fileNames = Object.keys(zip.files);
        if (fileNames.length > 0) {
          const firstFile = zip.files[fileNames[0]];
          const content = await firstFile.async("string");
          setGcodeFull(content);
          setGcodeTotalLines(content.split("\n").length);
          setGcodePreview(content.split("\n").slice(0, 50).join("\n"));
        }
      }
    };

    ws.onerror = (e) => {
      console.error("WebSocket error", e);
    };

    return () => {
      try{ ws.close(); }catch(e){};
      wsRef.current = null;
    };
  }, []);

  // helper to send base64 image and options
  const sendImage = async (file: File, options: any = {}) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      throw new Error("WebSocket not connected");
    }
    return new Promise<void>((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        try {
          const b64 = (reader.result as string).split(",")[1];
          wsRef.current!.send(JSON.stringify({ file_base64: b64, ...options }));
          resolve();
        } catch (e) { reject(e); }
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };

  return { progress, zipFile, gcodePreview, gcodeFull, gcodeTotalLines, setGcodePreview, sendImage };
}

"use client";
import { useState } from "react";
import useWebSocketProgress from "@/hooks/useWebSocketProgress";

export default function BeginnerMode({ machine, setMachine, showSnackbar }:{ machine:string, setMachine:(m:string)=>void, showSnackbar?: (msg:string,type?:"success"|"error")=>void }) {
  const [image, setImage] = useState<string|null>(null);
  const { progress, zipFile, sendImage } = useWebSocketProgress();

  const handleGenerate = async (fileInput?: HTMLInputElement) => {
    if (!fileInput || !fileInput.files || !fileInput.files[0]) { 
      showSnackbar ? showSnackbar("❌ يجب رفع صورة أولا", "error") : alert("يجب رفع صورة"); 
      return; 
    }
    const file = fileInput.files[0];
    try{
      await sendImage(file, { machine });
      showSnackbar && showSnackbar(`✅ جاري توليد G-code للماكينة: ${machine}`, "success");
    }catch(e){
      showSnackbar && showSnackbar(`❌ فشل الإرسال: ${e}`, "error");
    }
  };

  return (
    <div className="p-6 bg-white rounded shadow max-w-md mx-auto">
      <h2 className="text-xl font-bold mb-4">Beginner Mode</h2>

      <div className="mb-4">
        <label className="block mb-2">ارفع صورة</label>
        <input id="beg-file" type="file" accept="image/*" onChange={(e)=>{
          if(e.target.files && e.target.files[0]){
            setImage(URL.createObjectURL(e.target.files[0]));
          }
        }}/>
      </div>

      <div className="mb-4">
        <label className="block mb-2">اختر الماكينة</label>
        <select value={machine} onChange={(e)=>setMachine(e.target.value)}
          className="border rounded px-2 py-1">
          <option value="router">Router (Wood/Plastic/Metal)</option>
          <option value="laser">Laser (Wood/Acrylic)</option>
          <option value="plasma">Plasma (Steel/Aluminum)</option>
        </select>
      </div>

      <button onClick={()=>handleGenerate(document.getElementById('beg-file') as HTMLInputElement)} className="px-4 py-2 bg-blue-600 text-white rounded">
        توليد G-code
      </button>

      {progress>0 && (
        <div className="mt-4">
          <div className="text-sm text-gray-600">التقدم: {progress}%</div>
          <div className="w-full bg-gray-200 rounded h-2 mt-1">
            <div className="bg-green-500 h-2 rounded" style={{width:progress+"%"}}></div>
          </div>
        </div>
      )}

      {zipFile && (
        <div className="mt-4">
          <a href={URL.createObjectURL(zipFile)} download="cnc_gcode.zip" className="px-3 py-1 bg-green-600 text-white rounded">
            تحميل G-code (ZIP)
          </a>
        </div>
      )}
    </div>
  );
}

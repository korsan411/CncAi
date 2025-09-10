export default function SettingsPanel({ machine, config, onChange, showSnackbar }:{
  machine:string,
  config:any,
  onChange:(cfg:any)=>void,
  showSnackbar?: (msg:string,type?:"success"|"error")=>void
}) {
  const handleFeedChange = (val:string) => {
    const feed = parseInt(val||"0");
    if(feed <= 0){
      showSnackbar && showSnackbar("❌ Feedrate غير صالح", "error");
      return;
    }
    onChange({...config, feed});
  };

  return (
    <div className="p-4 bg-white rounded shadow space-y-2">
      <h3 className="font-bold mb-2">إعدادات متقدمة ({machine})</h3>

      <div>
        <label className="block mb-1">المادة (Material)</label>
        <select value={config.material} onChange={e=>onChange({...config, material:e.target.value})}
          className="border rounded px-2 py-1">
          <option value="wood">Wood</option>
          <option value="plastic">Plastic</option>
          <option value="metal">Metal</option>
        </select>
      </div>

      <div>
        <label className="block mb-1">البروفايل (Post Processor)</label>
        <select value={config.profile} onChange={e=>onChange({...config, profile:e.target.value})}
          className="border rounded px-2 py-1">
          <option value="grbl">GRBL</option>
          <option value="marlin">Marlin</option>
          <option value="mach3">Mach3</option>
          <option value="linuxcnc">LinuxCNC</option>
        </select>
      </div>

      <div>
        <label className="block mb-1">قطر الأداة (Tool Diameter mm)</label>
        <input type="number" step="0.1" value={config.tool_diameter}
          onChange={e=>onChange({...config, tool_diameter:parseFloat(e.target.value)})}
          className="border rounded px-2 py-1 w-full"/>
      </div>

      <div>
        <label className="block mb-1">Kerf (mm)</label>
        <input type="number" step="0.01" value={config.kerf}
          onChange={e=>onChange({...config, kerf:parseFloat(e.target.value)})}
          className="border rounded px-2 py-1 w-full"/>
      </div>

      <div>
        <label className="block mb-1">Feedrate</label>
        <input type="number" value={config.feed}
          onChange={e=>handleFeedChange(e.target.value)}
          className="border rounded px-2 py-1 w-full"/>
      </div>
    </div>
  );
}

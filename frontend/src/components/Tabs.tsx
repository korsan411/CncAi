import React from 'react'
export function Tabs({tabs,active,onChange}){
  return (<div className='flex gap-2 mb-4'>{tabs.map(t=>(<button key={t.id} onClick={()=>onChange(t.id)} className={'px-4 py-2 rounded '+(active===t.id?'bg-slate-900 text-white':'bg-slate-200')}>{t.label}</button>))}</div>)
}

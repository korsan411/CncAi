import React,{useState} from 'react'
export default function BeginnerMode(){
  const [file,setFile]=useState(null)
  return (<div><input type='file' onChange={e=>setFile(e.target.files?.[0]||null)} /><div>{file?file.name:'لم يتم اختيار ملف'}</div></div>)
}

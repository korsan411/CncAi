import React, { useState } from 'react'
import { Tabs } from './components/Tabs'
import BeginnerMode from './components/BeginnerMode'

export default function App(){
  const [active, setActive] = useState('beginner')
  const tabs = [{id:'beginner',label:'الوضع المبسط'}]
  return (<div className='p-4'><h1 className='text-2xl font-bold mb-4'>CNCai</h1><Tabs tabs={tabs} active={active} onChange={setActive} />{active==='beginner' && <BeginnerMode />}</div>)
}

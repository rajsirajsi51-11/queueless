export const API_BASE = import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.PROD ? 'https://queueless-api-dx66.onrender.com' : 'http://localhost:5000');
export async function api(path, options={}) {
  const demoUid=localStorage.getItem('queueless-demo-uid');
  const headers={'Content-Type':'application/json',...(demoUid?{'X-Dev-Uid':demoUid}:{}),...(options.headers||{})};
  let response;
  try { response=await fetch(`${API_BASE}${path}`,{...options,headers}); }
  catch { throw new Error('Backend unavailable. Check your connection and try again.'); }
  const body=await response.json().catch(()=>({error:{message:'Unexpected server response'}}));
  if(!response.ok) throw new Error(body.error?.message || body.message || 'Request failed');
  return body.data;
}
